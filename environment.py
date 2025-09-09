# environment.py
import random
import pandas as pd
from typing import List, Tuple
from agents import Agent
from managers import LeaderElection, ReputationManager, CommsManager

class Environment:
    def __init__(
        self,
        n_agents: int = 8,
        area_size: Tuple[float,float] = (30.0, 30.0),
        seed: int = 42,
        failure_prob: float = 0.02,
        low_priority_cutoff: int = 20,
        leader_weights=(0.4,0.3,0.3),
        rep_threshold: float = 0.25
    ):
        random.seed(seed)
        self.n_agents = n_agents
        self.area_size = area_size
        self.failure_prob = failure_prob
        self.low_priority_cutoff = low_priority_cutoff
        self.agents: List[Agent] = []
        self.time = 0
        self.logs = []
        self.metrics = {"messages_sent": 0, "messages_dropped": 0, "leader_changes": 0}
        self.leader_manager = LeaderElection(weights=leader_weights, rep_threshold=rep_threshold, reference_point=(area_size[0]/2, area_size[1]/2))
        self.rep_manager = ReputationManager()
        self.comms_manager = CommsManager(area_size=area_size, gamma=0.07)
        self._init_agents()

    def _init_agents(self):
        self.agents = []
        for i in range(self.n_agents):
            pos = (random.uniform(0, self.area_size[0]), random.uniform(0, self.area_size[1]))
            battery = random.uniform(0.6, 1.0)
            a = Agent(id=i, pos=pos, battery=battery)
            self.rep_manager.initialize(a)
            self.agents.append(a)
        # elect initial leader
        leader = self.leader_manager.elect(self.agents)
        for a in self.agents:
            a.is_leader = (a.id == leader)

    def current_leader_id(self):
        for a in self.agents:
            if a.is_leader:
                return a.id
        return None

    def step(self, step_idx: int, move_step: float = 0.8):
        self.time = step_idx
        # 1. Movement and battery drain
        for a in self.agents:
            if not a.alive:
                continue
            if random.random() < 0.6:
                a.random_walk(self.area_size, step_size=move_step)
            else:
                a.move_towards((self.area_size[0]/2, self.area_size[1]/2), step_size=move_step)
            a.drain_battery(amount=0.005 + random.random() * 0.01)

        # 2. Update comm qualities (based on current leader position)
        leader_id = self.current_leader_id()
        leader_pos = None
        if leader_id is not None:
            leader_pos = next((x.pos for x in self.agents if x.id == leader_id), None)
        for a in self.agents:
            self.comms_manager.update_comm_quality(a, leader_pos=leader_pos)

        # 3. Agents attempt to broadcast status (simulate sends)
        statuses = []
        for a in self.agents:
            sent = a.attempt_send(priority="NORMAL", swarm_size=self.n_agents, low_cutoff=self.low_priority_cutoff)
            if sent:
                statuses.append(a.id)
                self.metrics["messages_sent"] += 1
            else:
                self.metrics["messages_dropped"] += 1
            # reputation manager uses the fact they sent (or not)
            self.rep_manager.update_from_send(a, sent)

        available_ids = set(statuses)

        # 4. Elect leader (penalizing missing broadcasters)
        prev_leader = self.current_leader_id()
        new_leader = self.leader_manager.elect(self.agents, available_ids=available_ids)
        if new_leader != prev_leader and new_leader is not None:
            self.metrics["leader_changes"] += 1
        for a in self.agents:
            a.is_leader = (a.id == new_leader)

        # 5. Random failures (battery exhaustion already handled), additional failure injection
        for a in self.agents:
            if a.alive and random.random() < self.failure_prob:
                a.alive = False
                a.battery = 0.0
                # immediate penalty
                self.rep_manager.update_for_failure(a)

        # 6. Log step
        self._log_step(step_idx, new_leader)
        return new_leader

    def _log_step(self, step_idx: int, leader_id: int):
        row = {
            "step": step_idx,
            "leader": leader_id,
            "messages_sent": self.metrics["messages_sent"],
            "messages_dropped": self.metrics["messages_dropped"],
            "leader_changes": self.metrics["leader_changes"]
        }
        for a in self.agents:
            row[f"agent_{a.id}_pos_x"] = a.pos[0]
            row[f"agent_{a.id}_pos_y"] = a.pos[1]
            row[f"agent_{a.id}_battery"] = a.battery
            row[f"agent_{a.id}_rep"] = a.reputation()
            row[f"agent_{a.id}_alive"] = a.alive
        self.logs.append(row)

    def run(self, steps: int = 100, verbose: bool = False):
        # Reset logs and metrics
        self.logs = []
        self.metrics = {"messages_sent": 0, "messages_dropped": 0, "leader_changes": 0}
        # reinitialize agents for a fresh start
        self._init_agents()
        for t in range(steps):
            leader = self.step(t)
            if verbose:
                print(f"Step {t}: leader {leader}")
        return pd.DataFrame(self.logs)
