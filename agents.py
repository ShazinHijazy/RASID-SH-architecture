# agents.py
import math
import random
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Agent:
    id: int
    pos: Tuple[float, float]
    battery: float = 1.0
    comm_quality: float = 1.0       # instantaneous comm quality (0..1)
    rep_success: int = 1            # Bayesian prior (Beta(1,1))
    rep_failure: int = 1
    is_leader: bool = False
    alive: bool = True
    msgs_sent: int = 0
    msgs_dropped: int = 0
    task_done: int = 0              # optional task counter

    def status(self) -> dict:
        return {
            "id": self.id,
            "pos": (round(self.pos[0], 3), round(self.pos[1], 3)),
            "battery": round(self.battery, 4),
            "comm": round(self.comm_quality, 4),
            "rep": round(self.reputation(), 4),
            "alive": self.alive,
            "is_leader": self.is_leader
        }

    def reputation(self) -> float:
        # Bayesian posterior mean for Beta(success+1, failure+1)
        return (self.rep_success) / (self.rep_success + self.rep_failure)

    def random_walk(self, bounds: Tuple[float, float], step_size: float = 0.5):
        if not self.alive:
            return
        ang = random.random() * 2 * math.pi
        nx = self.pos[0] + math.cos(ang) * step_size
        ny = self.pos[1] + math.sin(ang) * step_size
        nx = max(0, min(bounds[0], nx))
        ny = max(0, min(bounds[1], ny))
        self.pos = (nx, ny)

    def move_towards(self, goal: Tuple[float, float], step_size: float = 0.5):
        if not self.alive:
            return
        dx = goal[0] - self.pos[0]
        dy = goal[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return
        nx = self.pos[0] + (dx / dist) * min(step_size, dist)
        ny = self.pos[1] + (dy / dist) * min(step_size, dist)
        self.pos = (nx, ny)

    def drain_battery(self, amount: float):
        if not self.alive:
            return
        self.battery -= amount
        if self.battery <= 0:
            self.battery = 0
            self.alive = False

    def compute_score(self, reference_point=(0, 0), weights=(0.4, 0.3, 0.3), eps_max=0.01):
        # score = w_b*b + w_d*(1/(1+dist)) + w_c * comm + eps
        if not self.alive:
            return -float("inf")
        w_b, w_d, w_c = weights
        dist = math.hypot(self.pos[0] - reference_point[0], self.pos[1] - reference_point[1])
        dist_score = 1.0 / (1.0 + dist)
        eps = random.uniform(0, eps_max)
        return w_b * self.battery + w_d * dist_score + w_c * self.comm_quality + eps

    def bayesian_update(self, success: bool):
        if success:
            self.rep_success += 1
        else:
            self.rep_failure += 1

    def attempt_send(self, priority="NORMAL", swarm_size=5, low_cutoff=20, gamma=0.02):
        """
        Determine whether a message is sent successfully.
        - If LOW priority and swarm large -> higher drop probability.
        - comm_quality directly factors into send probability.
        Returns True if 'sent', False if dropped.
        """
        if not self.alive:
            self.msgs_dropped += 1
            return False
        if priority == "LOW" and swarm_size > low_cutoff:
            drop_prob = min(0.95, 0.5 + (swarm_size - low_cutoff) * gamma)
            if random.random() < drop_prob:
                self.msgs_dropped += 1
                return False
        # simulate communication noise using comm_quality
        if random.random() > self.comm_quality:
            self.msgs_dropped += 1
            return False
        self.msgs_sent += 1
        return True
