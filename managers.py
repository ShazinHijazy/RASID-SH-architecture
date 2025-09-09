# managers.py
import math
import random
from typing import List, Tuple
from agents import Agent

class LeaderElection:
    def __init__(self, weights=(0.4,0.3,0.3), rep_threshold=0.25, reference_point=(0,0)):
        self.weights = weights
        self.rep_threshold = rep_threshold
        self.reference_point = reference_point

    def elect(self, agents: List[Agent], available_ids: set = None):
        """
        Elects a leader among alive agents with reputation >= threshold.
        If available_ids provided (agents who successfully broadcasted),
        penalize those not present by multiplying their score by 0.8.
        """
        candidates = []
        for a in agents:
            if not a.alive:
                continue
            if a.reputation() < self.rep_threshold:
                continue
            base_score = a.compute_score(reference_point=self.reference_point, weights=self.weights)
            if available_ids is not None and a.id not in available_ids:
                base_score *= 0.8  # penalize missing broadcasters
            candidates.append((a, base_score))
        if not candidates:
            return None
        best, _ = max(candidates, key=lambda x: x[1])
        return best.id

class ReputationManager:
    def __init__(self, prior_success=1, prior_fail=1):
        self.prior_success = prior_success
        self.prior_fail = prior_fail

    def initialize(self, agent: Agent):
        agent.rep_success = self.prior_success
        agent.rep_failure = self.prior_fail

    def update_from_send(self, agent: Agent, sent: bool):
        # Sent -> success roughly, not perfect (network can drop).
        # We treat sent==True as positive evidence for reliability.
        agent.bayesian_update(success=sent)

    def update_for_failure(self, agent: Agent):
        agent.bayesian_update(success=False)

class CommsManager:
    def __init__(self, area_size: Tuple[float,float], gamma=0.05):
        self.area_size = area_size
        self.gamma = gamma  # distance decay factor for comm quality

    def update_comm_quality(self, agent: Agent, leader_pos: Tuple[float,float] = None):
        # Basic model: quality = exp(-gamma * distance_to_leader); clamp [0.01, 1]
        if not agent.alive:
            agent.comm_quality = 0.0
            return
        if leader_pos is None:
            # measure to swarm center
            center = (self.area_size[0]/2, self.area_size[1]/2)
            dist = math.hypot(agent.pos[0]-center[0], agent.pos[1]-center[1])
        else:
            dist = math.hypot(agent.pos[0]-leader_pos[0], agent.pos[1]-leader_pos[1])
        q = math.exp(-self.gamma * dist)
        # add small randomness to simulate fading / noise
        q = max(0.01, min(1.0, q * (0.9 + 0.2 * random.random())))
        agent.comm_quality = q
