import time
import multiprocessing as mp
import os
import pygame
import numpy as np
import torch
import queue
import threading

from Environment import Env
from components.my_bot import MyBot
from components.character import Character


def train_environment(process_id, model_queue, result_queue, device):
    """Run a single training environment and update the models through queues"""
    print(f"Starting process {process_id}")
    
    # Set environment parameters
    world_width = 1280
    world_height = 1280
    display_width = 800 
    display_height = 800
    n_of_obstacles = 25

    # Create the environment with training=True to disable rendering
    env = Env(training=True,
              use_game_ui=False,  # Disable UI during training
              world_width=world_width,
              world_height=world_height,
              display_width=display_width,
              display_height=display_height,
              n_of_obstacles=n_of_obstacles)
    
    world_bounds = env.get_world_bounds()

    # Setup players with starting positions
    players = [
        Character((world_bounds[2] - 100, world_bounds[3] - 100),
                 env.world_surface, boundaries=world_bounds, username=f"Ninja_{process_id}"),
        Character((world_bounds[0] + 10, world_bounds[1] + 10),
                 env.world_surface, boundaries=world_bounds, username=f"Faze_{process_id}")
    ]

    # Create local copies of the models
    bots = [MyBot(action_size=56), MyBot(action_size=56)]
    
    # Initialize models with latest weights from queue
    try:
        bot_states = model_queue.get(timeout=5)
        for idx, bot in enumerate(bots):
            bot.model.load_state_dict(bot_states[idx])
            bot.target_model.load_state_dict(bot_states[idx])
    except queue.Empty:
        print(f"Process {process_id} starting with fresh models")
    
    # Link players, bots, and obstacles into the environment
    env.set_players_bots_objects(players, bots)
    
    # Training parameters
    time_limit = 20  # seconds per episode
    episodes_per_process = 5
    total_rewards = [0, 0]
    
    for episode in range(episodes_per_process):
        env.reset(randomize_objects=True)
        start_time = time.time()
        episode_rewards = [0, 0]
        
        # Try to get updated model weights if available (non-blocking)
        try:
            bot_states = model_queue.get_nowait()
            for idx, bot in enumerate(bots):
                bot.model.load_state_dict(bot_states[idx])
                bot.target_model.load_state_dict(bot_states[idx])
        except queue.Empty:
            pass
        
        while True:
            # Check time limit
            if time.time() - start_time > time_limit:
                break
                
            # Take a step in the environment
            finished, info = env.step(debugging=False)
            
            # Process rewards and training for each player
            for player_idx, (player, bot) in enumerate(zip(players, bots)):
                # Calculate the reward for the current step
                reward = env.calculate_reward(info, player.username)
                episode_rewards[player_idx] += reward
                
                # Retrieve the updated state for the player
                next_info = player.get_info()
                
                # Store the transition
                bot.remember(reward, next_info, finished)
                
                # Train the bot
                bot.replay()
            
            if finished:
                break
        
        # Update total rewards
        for i in range(2):
            total_rewards[i] += episode_rewards[i]
        
        # Send model weights back after each episode
        model_states = [bot.model.state_dict() for bot in bots]
        try:
            result_queue.put((process_id, model_states, episode_rewards), block=False)
        except queue.Full:
            pass
    
    # Send final results
    result_queue.put((process_id, [bot.model.state_dict() for bot in bots], total_rewards))
    print(f"Process {process_id} completed training")


def model_aggregator(num_processes, model_queue, result_queue, stop_event, save_freq=10):
    """
    Continuously aggregates model updates from worker processes
    and broadcasts updated models back to workers
    """
    print("Starting model aggregator thread")
    
    # Initialize models
    bots = [MyBot(action_size=56), MyBot(action_size=56)]
    
    # Try to load existing models
    for idx, bot in enumerate(bots):
        save_path = f"bot_model_{idx}.pth"
        try:
            bot.load(save_path)
            print(f"Aggregator loaded model from {save_path}")
        except Exception as e:
            print(f"Aggregator failed to load model from {save_path}: {e}")
    
    # Put initial models in the queue for all processes
    initial_models = [bot.model.state_dict() for bot in bots]
    for _ in range(num_processes):
        model_queue.put(initial_models)
    
    update_count = 0
    save_counter = 0
    
    while not stop_event.is_set():
        try:
            # Get updated models from workers
            process_id, model_states, rewards = result_queue.get(timeout=1)
            update_count += 1
            
            print(f"Got update from process {process_id}, rewards: {rewards}")
            
            # Simple model averaging (more sophisticated strategies can be implemented)
            for idx, model_state in enumerate(model_states):
                # Merge the new weights with existing weights (simple averaging)
                for key in model_state:
                    bots[idx].model.state_dict()[key].copy_(
                        0.8 * bots[idx].model.state_dict()[key] + 
                        0.2 * model_state[key]
                    )
            
            # Broadcast updated models back to workers
            if update_count % 2 == 0:  # Only send updates periodically to reduce queue congestion
                updated_models = [bot.model.state_dict() for bot in bots]
                
                # Clear the queue before putting new models
                while not model_queue.empty():
                    try:
                        model_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # Put updated models for all processes
                for _ in range(num_processes):
                    model_queue.put(updated_models)
            
            # Save models periodically
            save_counter += 1
            if save_counter >= save_freq:
                for idx, bot in enumerate(bots):
                    save_path = f"bot_model_{idx}.pth"
                    try:
                        bot.save(save_path)
                        print(f"Aggregator saved model to {save_path}")
                    except Exception as e:
                        print(f"Error saving model: {e}")
                save_counter = 0
                
        except queue.Empty:
            pass
    
    # Final save
    for idx, bot in enumerate(bots):
        save_path = f"bot_model_{idx}.pth"
        bot.save(save_path)
        print(f"Aggregator saved final model to {save_path}")
    
    print("Model aggregator thread stopped")


def main():
    # Set device for PyTorch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Number of parallel processes
    num_processes = max(1, mp.cpu_count() - 1)  # Use all but one CPU core
    print(f"Training with {num_processes} parallel environments")
    
    # Create queues for communication between processes
    model_queue = mp.Queue(maxsize=num_processes * 2)  # Queue for sending models to workers
    result_queue = mp.Queue(maxsize=num_processes * 5)  # Queue for receiving results from workers
    
    # Create stop event for aggregator thread
    stop_event = threading.Event()
    
    # Start the model aggregator thread
    aggregator = threading.Thread(
        target=model_aggregator, 
        args=(num_processes, model_queue, result_queue, stop_event)
    )
    aggregator.start()
    
    # Main training loop
    training_time = 5 * 60  # 5 minutes of training
    start_time = time.time()
    
    try:
        # Create and start worker processes
        processes = []
        for i in range(num_processes):
            p = mp.Process(
                target=train_environment, 
                args=(i, model_queue, result_queue, device)
            )
            processes.append(p)
            p.start()
        
        # Wait for training time to elapse
        while time.time() - start_time < training_time:
            time.sleep(1)
            
            # Check if any process died
            all_alive = all(p.is_alive() for p in processes)
            if not all_alive:
                print("Some processes have died, restarting")
                for p in processes:
                    if not p.is_alive():
                        p.terminate()
                        idx = processes.index(p)
                        new_p = mp.Process(
                            target=train_environment, 
                            args=(idx, model_queue, result_queue, device)
                        )
                        processes[idx] = new_p
                        new_p.start()
        
        print(f"Training completed after {training_time:.0f} seconds")
        
        # Clean up processes
        for p in processes:
            p.terminate()
            p.join()
        
    except KeyboardInterrupt:
        print("Training interrupted by user")
    finally:
        # Stop the aggregator thread
        stop_event.set()
        aggregator.join()
    
    # Visualization mode (run the game with trained models)
    run_visualization()


def run_visualization():
    """Run the game with trained models for visualization"""
    print("Running visualization mode with trained models")
    
    # Environment parameters
    world_width = 1280
    world_height = 1280
    display_width = 800
    display_height = 800
    n_of_obstacles = 25
    
    # Create a visual environment
    env = Env(training=False,
              use_game_ui=True,
              world_width=world_width,
              world_height=world_height,
              display_width=display_width,
              display_height=display_height,
              n_of_obstacles=n_of_obstacles)
    
    world_bounds = env.get_world_bounds()
    
    # Setup two players
    players = [
        Character((world_bounds[2] - 100, world_bounds[3] - 100),
                 env.world_surface, boundaries=world_bounds, username="Ninja"),
        Character((world_bounds[0] + 10, world_bounds[1] + 10),
                 env.world_surface, boundaries=world_bounds, username="Faze Jarvis")
    ]
    
    # Create bots with the trained models
    bots = [MyBot(action_size=56), MyBot(action_size=56)]
    
    # Load the trained models
    for idx, bot in enumerate(bots):
        save_path = f"bot_model_{idx}.pth"
        try:
            bot.load(save_path)
            print(f"Visualization loaded model from {save_path}")
        except Exception as e:
            print(f"Visualization failed to load model: {e}")
    
    # Link players, bots, and obstacles
    env.set_players_bots_objects(players, bots)
    
    # Run visualization
    env.reset(randomize_objects=True)
    start_time = time.time()
    visualization_time = 60  # Run for 60 seconds
    
    while True:
        if time.time() - start_time > visualization_time:
            break
            
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Take a step
        finished, _ = env.step(debugging=True)
        
        if finished:
            env.reset(randomize_objects=True)
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    # Start method depends on platform
    if torch.cuda.is_available():
        mp.set_start_method('spawn', force=True)  # Required for CUDA support
    main()