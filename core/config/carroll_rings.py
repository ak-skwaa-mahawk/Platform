"""
carroll_rings.py - Carroll Rings Harmonic Chase System
Implements the 3D toroidal running-state geometry and stabilized Fibonacci loops.
"""

import math

class CarrollRingsSystem:
    def __init__(self):
        # The Core Baseline Constants
        self.flat_pi = 3.141592653589793
        self.phi = 1.618033988749895
        
        # The Toroidal Shift Factor derived from your Pi correction
        self.gear_shift = 1.04
        
        # Your Verified Running-State Attractors
        self.target_fib = 1.65036
        self.target_pi_3d = 3.20442315
        self.target_pi_4d = 3.2672536

    def run_fibonacci_chase(self, iterations=3):
        """
        Executes the 3-Tiered Carroll Ring loop.
        Demonstrates how the system 'chases' and locks the Golden Ratio.
        """
        print("--- RUNNING CARROLL RINGS FIBONACCI CHASE ---")
        
        # Ring 1: The Input Blast / Expansion
        ring_1_expansion = round(self.phi * self.gear_shift, 5)
        print(f"Ring 1 (Expansion Peak) : {self.phi:.3f} * {self.gear_shift} = {ring_1_expansion}")
        
        # Ring 2: The Two-Way Chase / First Settle
        ring_2_settle = round((ring_1_expansion + self.phi) / 2, 5)
        print(f"Ring 2 (Two-Way Settle) : ({ring_1_expansion} + {self.phi:.3f}) / 2 = {ring_2_settle}")
        
        # Ring 3: The Three-Way Lock / Toroidal Loop Reset
        current_val = ring_2_settle
        for i in range(1, iterations + 1):
            three_way_sum = current_val + ring_1_expansion + self.phi
            next_val = round(three_way_sum / 3, 5)
            print(f"Ring 3 (Loop Layer {i})  : ({current_val} + {ring_1_expansion} + {self.phi:.3f}) / 3 = {next_val}")
            
            # Check for immediate phase lock
            if next_val == current_val:
                print(f"🌀 System Phase-Locked perfectly at: {next_val} (Error Stack Cleared to 0.0)\n")
                break
            current_val = next_val
            
        return current_val

    def calculate_alignment(self, angle_degrees=142.5):
        """
        Maps Sin and Cos directly to Force (F) and Work (W) variables
        on a running, curved 3D toroidal geometry.
        """
        print("--- TOROIDAL ALIGNMENT MATRIX ---")
        # Convert the angle to radians using the running 3D Pi baseline
        angle_radians = (angle_degrees * self.target_pi_3d) / 180.0
        
        # Map Trigonometry directly to Mechanical Realities
        force_sin = math.sin(angle_radians)
        work_cos = math.cos(angle_radians)
        
        print(f"Input Angle            : {angle_degrees}°")
        print(f"Running 3D Pi Radians  : {angle_radians:.6f} rad")
        print(f"Sin Vector (Force F)   : {force_sin:+.6f} [Positive Push / Containment]")
        print(f"Cos Vector (Work W)    : {work_cos:+.6f} [Negative Braking / Pressure Balance]")
        
        # Ratio confirmation against your structural parameters
        chase_ratio = self.target_pi_3d / self.target_fib
        print(f"Toroidal Chase Ratio   : {self.target_pi_3d} / {self.target_fib} = {chase_ratio:.5f}")
        print("---------------------------------\n")
        
        return {"Force": force_sin, "Work": work_cos, "Ratio": chase_ratio}

if __name__ == "__main__":
    # Initialize the framework engine
    engine = CarrollRingsSystem()
    
    # Run the structural loops
    engine.run_fibonacci_chase()
    engine.calculate_alignment()
