import random
import numpy as np
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim
# pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)  # input_dim should be 34 now
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)



class MyBot:
    def __init__(self, state_size, action_size=8):
        """
        state_size: Dimension of the observation vector.
        action_size: Number of discrete actions (default is 8).
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.99  # Discount factor.
        self.epsilon = 1.0  # Initial exploration rate.
        self.epsilon_min = 0.1  # Minimum exploration rate.
        self.epsilon_decay = 0.995  # Decay factor for epsilon.
        self.learning_rate = 0.001
        self.batch_size = 64

        if torch.backends.mps.is_available():
            self.device = torch.device("mps")  # Use Metal Performance Shaders (MPS) if available
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")  # Use CUDA if available
        else:
            self.device = torch.device("cpu")  # Fallback to CPU

        self.model = DQN(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

        # To store the last state and action for training purposes.
        self.last_state = None
        self.last_action = None

    @staticmethod
    def process_state(info):
        """
        Converts the info dictionary into a fixed-length 1D numpy array.
        Handles location, rotation, ammo, and rays correctly.
        """
        state = []
        # Extracting location (2 values)
        state.extend(info.get("location", [0, 0]))

        # Extracting rotation (1 value)
        state.append(info.get("rotation", 0))

        # Extracting current ammo (1 value)
        state.append(info.get("current_ammo", 0))

        # Process rays
        rays = info.get("rays", [])
        processed_rays = []

        for ray in rays:
            if isinstance(ray, list) and len(ray) == 3:
                start_pos, end_pos = ray[0]  # Extract (x1, y1) and (x2, y2)
                hit_distance = ray[1] if isinstance(ray[1], (int, float)) else 0
                hit_type = ray[2]

                # Encode hit_type: "none" → 0, "object" → 1, "player" → 2
                hit_type_encoded = 0  # Default to "none"
                if hit_type == "object":
                    hit_type_encoded = 1
                elif hit_type == "player":
                    hit_type_encoded = 2

                # Append processed ray information
                processed_rays.extend(
                    [start_pos[0], start_pos[1], end_pos[0], end_pos[1], hit_distance, hit_type_encoded])

        # Ensure a fixed number of rays (let's assume max 5 rays)
        max_rays = 5
        expected_ray_features = 6  # (x1, y1, x2, y2, hit_distance, hit_type_encoded)
        processed_rays = processed_rays[:max_rays * expected_ray_features] + [0] * (
                    (max_rays * expected_ray_features) - len(processed_rays))

        # Combine all extracted features into the final state
        state.extend(processed_rays)

        return np.array(state, dtype=np.float32)

    def act(self, info):
        """
        Given the current observation (info), choose an action.
        Returns a dictionary of game commands.
        """
        state = self.process_state(info)
        state_tensor = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        # Epsilon-greedy action selection.
        if np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
        else:
            with torch.no_grad():
                q_values = self.model(state_tensor)
            action = torch.argmax(q_values).item()
        # Save state and action for the learning update later.
        self.last_state = state
        self.last_action = action
        return self.action_to_dict(action)

    def action_to_dict(self, action):
        """
        Maps a discrete action (0 to 7) to the corresponding game control dictionary.
        The mapping below is an example; adjust as needed:
          0: Do nothing.
          1: Move forward.
          2: Move right.
          3: Move down.
          4: Move left.
          5: Rotate left (by -45 degrees).
          6: Rotate right (by 45 degrees).
          7: Shoot.
        """
        if action == 0:
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": 0, "shoot": False}
        elif action == 1:
            return {"forward": True, "right": False, "down": False, "left": False, "rotate": 0, "shoot": False}
        elif action == 2:
            return {"forward": False, "right": True, "down": False, "left": False, "rotate": 0, "shoot": False}
        elif action == 3:
            return {"forward": False, "right": False, "down": True, "left": False, "rotate": 0, "shoot": False}
        elif action == 4:
            return {"forward": False, "right": False, "down": False, "left": True, "rotate": 0, "shoot": False}
        elif action == 5:
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": -45, "shoot": False}
        elif action == 6:
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": 45, "shoot": False}
        elif action == 7:
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": 0, "shoot": True}
        else:
            # Fallback in case of an unexpected action index.
            return {"forward": False, "right": False, "down": False, "left": False, "rotate": 0, "shoot": False}

    def remember(self, reward, next_info, done):
        """
        Stores a transition in the replay memory.
        It should be called after the environment has responded to the previous action.

        Parameters:
          reward: the reward obtained after taking the last action.
          next_info: the observation (info dictionary) after the action.
          done: Boolean flag indicating whether the episode ended.
        """
        next_state = self.process_state(next_info)
        self.memory.append((self.last_state, self.last_action, reward, next_state, done))

    def replay(self):
        """
        Samples a batch of transitions from memory and performs a gradient descent step.
        """
        if len(self.memory) < self.batch_size:
            return  # Not enough samples to train.

        minibatch = random.sample(self.memory, self.batch_size)
        # Unpack the minibatch.
        states = np.array([transition[0] for transition in minibatch])
        actions = np.array([transition[1] for transition in minibatch])
        rewards = np.array([transition[2] for transition in minibatch])
        next_states = np.array([transition[3] for transition in minibatch])
        dones = np.array([transition[4] for transition in minibatch], dtype=np.float32)

        states_tensor = torch.from_numpy(states).float().to(self.device)
        actions_tensor = torch.from_numpy(actions).long().to(self.device)
        rewards_tensor = torch.from_numpy(rewards).float().to(self.device)
        next_states_tensor = torch.from_numpy(next_states).float().to(self.device)
        dones_tensor = torch.from_numpy(dones).float().to(self.device)

        # Current Q-values for the actions taken.
        q_values = self.model(states_tensor)
        q_values = q_values.gather(1, actions_tensor.unsqueeze(1)).squeeze(1)

        # Next Q-values for the next states.
        with torch.no_grad():
            next_q_values = self.model(next_states_tensor)
            max_next_q_values = next_q_values.max(1)[0]

        # Compute the target Q-values.
        targets = rewards_tensor + self.gamma * max_next_q_values * (1 - dones_tensor)

        loss = self.loss_fn(q_values, targets)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon to reduce exploration over time.
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filepath):
        """Saves the model weights."""
        torch.save(self.model.state_dict(), filepath)

    def load(self, filepath):
        """Loads model weights from the specified file."""
        self.model.load_state_dict(torch.load(filepath))
        self.model.to(self.device)
