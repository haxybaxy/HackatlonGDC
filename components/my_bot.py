import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from collections import deque
import random


class ImprovedDQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(ImprovedDQN, self).__init__()
        # Separate networks for different input types
        self.location_net = nn.Sequential(
            nn.Linear(2, 32),
            nn.ReLU()
        )

        self.status_net = nn.Sequential(
            nn.Linear(2, 32),  # rotation and ammo
            nn.ReLU()
        )

        self.ray_net = nn.Sequential(
            nn.Linear(30, 128),  # 5 rays * 6 features
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        # Combine all features
        self.combined_net = nn.Sequential(
            nn.Linear(128, 256),  # 32 + 32 + 64 = 128
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim)
        )

        # Initialize weights using Xavier initialization
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, state_dict):
        # Process different parts of the state separately
        loc = self.location_net(state_dict['location'])
        status = self.status_net(state_dict['status'])
        rays = self.ray_net(state_dict['rays'])

        # Combine all features
        combined = torch.cat([loc, status, rays], dim=1)
        return self.combined_net(combined)


class MyBot:
    def __init__(self, action_size=16):  # Increased action space
        self.action_size = action_size
        self.memory = deque(maxlen=100000)  # Increased memory size
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.05  # Lower minimum exploration
        self.epsilon_decay = 0.9995  # Slower decay
        self.learning_rate = 0.0003  # Reduced learning rate
        self.batch_size = 64  # Increased batch size for more stable learning
        self.min_memory_size = 1000  # Minimum memory size before starting training
        self.update_target_freq = 1000  # How often to update target network
        self.steps = 0

        # Device selection
        self.device = torch.device("cuda" if torch.cuda.is_available() else
                                   "mps" if torch.backends.mps.is_available() else
                                   "cpu")

        print(f"Using device: {self.device}")

        # Create two networks - one for current Q-values and one for target
        self.model = ImprovedDQN(input_dim=34, output_dim=action_size).to(self.device)
        self.target_model = ImprovedDQN(input_dim=34, output_dim=action_size).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='max',
                                                              factor=0.5, patience=5)

        self.last_state = None
        self.last_action = None
        self.training_started = False

    def normalize_state(self, info):
        """Normalize state values to improve learning stability"""
        try:
            state = {
                'location': torch.tensor([
                    info['location'][0] / 1280.0,  # Normalize by world width
                    info['location'][1] / 1280.0  # Normalize by world height
                ], dtype=torch.float32),

                'status': torch.tensor([
                    info['rotation'] / 360.0,  # Normalize rotation
                    info['current_ammo'] / 30.0  # Normalize ammo
                ], dtype=torch.float32),

                'rays': []
            }

            # Process rays
            ray_data = []
            for ray in info.get('rays', []):
                if isinstance(ray, list) and len(ray) == 3:
                    start_pos, end_pos = ray[0]
                    distance = ray[1] if ray[1] is not None else 1500  # Max vision distance
                    hit_type = ray[2]

                    # Normalize positions and distance
                    ray_data.extend([
                        start_pos[0] / 1280.0,
                        start_pos[1] / 1280.0,
                        end_pos[0] / 1280.0,
                        end_pos[1] / 1280.0,
                        distance / 1500.0,  # Normalize by max vision distance
                        1.0 if hit_type == "player" else 0.5 if hit_type == "object" else 0.0
                    ])

            # Pad rays if necessary
            while len(ray_data) < 30:  # 5 rays * 6 features
                ray_data.extend([0.0] * 6)

            state['rays'] = torch.tensor(ray_data[:30], dtype=torch.float32)
            return state

        except Exception as e:
            print(f"Error in normalize_state: {e}")
            print(f"Info received: {info}")
            raise

    def action_to_dict(self, action):
        """Enhanced action space with more granular rotation"""
        movement_directions = ["forward", "right", "down", "left"]
        rotation_angles = [-30, -5, -1, 0, 1, 5, 30]

        # Basic movement commands
        commands = {
            "forward": False,
            "right": False,
            "down": False,
            "left": False,
            "rotate": 0,
            "shoot": False
        }

        # determine block (no-shoot vs shoot)
        if action < 28:
            shoot = False
            local_action = action  # 0..27
        else:
            shoot = True
            local_action = action - 28  # 0..27

        movement_idx = local_action // 7  # 0..3
        angle_idx = local_action % 7  # 0..6

        direction = movement_directions[movement_idx]
        commands[direction] = True
        commands["rotate"] = rotation_angles[angle_idx]
        commands["shoot"] = shoot

        return commands

    def act(self, info):
        try:
            state = self.normalize_state(info)

            # Convert state dict to tensors and add batch dimension
            state_tensors = {
                k: v.unsqueeze(0).to(self.device) for k, v in state.items()
            }

            if random.random() <= self.epsilon:
                action = random.randrange(self.action_size)
            else:
                with torch.no_grad():
                    q_values = self.model(state_tensors)
                    action = torch.argmax(q_values).item()

            self.last_state = state
            self.last_action = action
            return self.action_to_dict(action)

        except Exception as e:
            print(f"Error in act: {e}")
            # Return safe default action
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": 0, "shoot": False}

    def remember(self, reward, next_info, done):
        try:
            next_state = self.normalize_state(next_info)
            self.memory.append((self.last_state, self.last_action, reward, next_state, done))

            # Start training only when we have enough samples
            if len(self.memory) >= self.min_memory_size and not self.training_started:
                print(f"Starting training with {len(self.memory)} samples in memory")
                self.training_started = True

            # Perform learning step if we have enough samples
            if self.training_started:
                self.replay()

            # Update target network periodically
            self.steps += 1
            if self.steps % self.update_target_freq == 0:
                self.target_model.load_state_dict(self.model.state_dict())
                print(f"Updated target network at step {self.steps}")

        except Exception as e:
            print(f"Error in remember: {e}")

    def replay(self):
        """Train the agent with randomly sampled batch from memory."""
        if len(self.memory) < self.min_memory_size:
            return  # Don't start training until we have enough samples

        if not self.training_started:
            print("Starting training...")
            self.training_started = True

        self.steps += 1

        # Update target network periodically
        if self.steps % self.update_target_freq == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        # Sample a batch of transitions from memory
        batch_size = min(self.batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)

        # Process the batch
        states, targets = [], []
        for state, action, reward, next_state, done in minibatch:
            # Convert states to tensor format
            state_tensor = self.state_to_tensors(state)
            
            # Get current Q values
            q_values = self.model(state_tensor).cpu().detach().numpy()
            
            if done:
                target = reward
            else:
                # Get next state Q values using target network for stability
                next_state_tensor = self.state_to_tensors(next_state)
                next_q_values = self.target_model(next_state_tensor).cpu().detach().numpy()
                target = reward + self.gamma * np.max(next_q_values)
            
            # Update target for the chosen action only
            target_f = q_values.copy()
            target_f[action] = target
            
            states.append(state)
            targets.append(target_f)

        # Convert to tensors for batch processing
        X = [self.state_to_tensors(s) for s in states]
        Y = [torch.tensor(t, dtype=torch.float32).to(self.device) for t in targets]

        # Train in batches of 8 to avoid CUDA memory issues
        sub_batch_size = 8
        for i in range(0, len(X), sub_batch_size):
            sub_X = X[i:i+sub_batch_size]
            sub_Y = Y[i:i+sub_batch_size]
            
            # Prepare batch data
            batch_loc = torch.stack([x['location'] for x in sub_X])
            batch_status = torch.stack([x['status'] for x in sub_X])
            batch_rays = torch.stack([x['rays'] for x in sub_X])
            
            # Forward pass
            self.optimizer.zero_grad()
            
            # Create input dictionary
            input_dict = {
                'location': batch_loc,
                'status': batch_status,
                'rays': batch_rays
            }
            
            # Get model output
            predictions = self.model(input_dict)
            
            # Compute loss
            targets_batch = torch.stack(sub_Y)
            loss = F.mse_loss(predictions, targets_batch)
            
            # Backward pass and optimize
            loss.backward()
            self.optimizer.step()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filepath):
        """Saves the model weights."""
        try:
            torch.save(self.model.state_dict(), filepath)
            print(f"Model saved successfully to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load(self, filepath):
        """Loads model weights from the specified file."""
        try:
            state_dict = torch.load(filepath, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.target_model.load_state_dict(state_dict)
            print(f"Model loaded successfully from {filepath}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Starting with a fresh model")
            # Initialize a fresh model if loading fails
            self.model = ImprovedDQN(input_dim=34, output_dim=self.action_size).to(self.device)
            self.target_model = ImprovedDQN(input_dim=34, output_dim=self.action_size).to(self.device)
            self.target_model.load_state_dict(self.model.state_dict())
            
    def sync_with_shared_model(self, shared_model):
        """Sync local model with shared model"""
        self.model.load_state_dict(shared_model.state_dict())
        self.target_model.load_state_dict(shared_model.state_dict())