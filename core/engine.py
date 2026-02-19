import os
import re
import json
import hashlib
from datetime import datetime

def extract_mld_from_prompt(prompt):
    """Extract MLD value from user prompt"""
    mld_match = re.search(r'(\d+)\s*MLD', prompt, re.IGNORECASE)
    return int(mld_match.group(1)) if mld_match else 10

def extract_number_from_prompt(prompt, keyword, default):
    """Extract a number following a keyword"""
    pattern = rf'{keyword}[:\s]*(\d+(?:\.\d+)?)'
    match = re.search(pattern, prompt, re.IGNORECASE)
    return float(match.group(1)) if match else default

def get_cad_code(user_prompt):
    """Generate REAL water treatment plant components based on prompt"""
    
    print(f"\n🔍 Processing: {user_prompt}")
    
    # Extract MLD for scaling
    mld = extract_mld_from_prompt(user_prompt)
    scale = (mld/10)**0.5
    
    # Create variation based on prompt
    seed = int(hashlib.md5(user_prompt.encode()).hexdigest()[:8], 16) % 1000
    variation = 0.8 + (seed / 1000.0)  # 0.8 to 1.8 variation
    
    prompt_lower = user_prompt.lower()
    
    # ============== COMPLETE WATER TREATMENT PLANT ==============
    if "complete" in prompt_lower or "full" in prompt_lower or "all units" in prompt_lower:
        print("🏭 Creating COMPLETE WATER TREATMENT PLANT")
        
        # Scale based on MLD
        spacing = 15 * scale
        
        # Calculate positions
        positions = [0, 12*scale, 25*scale, 40*scale, 55*scale, 72*scale]
        
        params = {
            "type": "complete_small_wtp",
            "description": f"Complete {mld} MLD water treatment plant",
            "capacity_mld": mld,
            "units": [
                {
                    "name": "Intake Structure",
                    "shape": "cylinder",
                    "radius": round(4 * scale, 2),
                    "height": round(8 * scale, 2),
                    "x": round(positions[0], 2),
                    "color": [0.2, 0.4, 0.8]
                },
                {
                    "name": "Flash Mixer",
                    "shape": "cylinder",
                    "radius": round(2.5 * scale, 2),
                    "height": round(4 * scale, 2),
                    "x": round(positions[1], 2),
                    "color": [0.8, 0.4, 0.2]
                },
                {
                    "name": "Flocculator",
                    "shape": "box",
                    "width": round(8 * scale, 2),
                    "depth": round(5 * scale, 2),
                    "height": round(4 * scale, 2),
                    "x": round(positions[2], 2),
                    "color": [0.3, 0.7, 0.5]
                },
                {
                    "name": "Clarifier",
                    "shape": "cylinder",
                    "radius": round(7 * scale, 2),
                    "height": round(6 * scale, 2),
                    "x": round(positions[3], 2),
                    "color": [0.1, 0.5, 0.9]
                },
                {
                    "name": "Rapid Sand Filter",
                    "shape": "box",
                    "width": round(7 * scale, 2),
                    "depth": round(5 * scale, 2),
                    "height": round(4 * scale, 2),
                    "x": round(positions[4], 2),
                    "color": [0.4, 0.7, 0.3]
                },
                {
                    "name": "Clear Water Tank",
                    "shape": "cylinder",
                    "radius": round(6 * scale, 2),
                    "height": round(7 * scale, 2),
                    "x": round(positions[5], 2),
                    "color": [0.2, 0.6, 0.9]
                }
            ],
            "connections": [
                {"from": 0, "to": 1, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 1, "to": 2, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 2, "to": 3, "radius": round(1.2 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 3, "to": 4, "radius": round(1.2 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 4, "to": 5, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)}
            ]
        }
    
    # ============== INDIVIDUAL COMPONENTS ==============
    elif "intake" in prompt_lower:
        print("🏭 Creating INTAKE STRUCTURE")
        params = {
            "type": "intake_structure",
            "description": "Raw water intake with screens",
            "components": [
                {"shape": "cylinder", "radius": round(3 * scale, 2), "height": round(8 * scale, 2), 
                 "x": 0, "y": 0, "z": 0},
                {"shape": "box", "width": round(6 * scale, 2), "depth": round(4 * scale, 2), 
                 "height": round(3 * scale, 2), "x": round(8 * scale, 2), "y": 0, "z": 0},
                {"shape": "pipe", "radius": round(1.0 * scale, 2), "length": round(10 * scale, 2), 
                 "x": round(4 * scale, 2), "y": 0, "z": round(2 * scale, 2)}
            ]
        }
    
    elif "clarifier" in prompt_lower:
        print("🏭 Creating CLARIFIER")
        params = {
            "type": "circular_clarifier",
            "description": "Circular clarifier with mechanical scraper",
            "components": [
                {"shape": "cylinder", "radius": round(8 * scale, 2), "height": round(5 * scale, 2), 
                 "x": 0, "y": 0, "z": 0},
                {"shape": "cylinder", "radius": round(2 * scale, 2), "height": round(2 * scale, 2), 
                 "x": 0, "y": 0, "z": round(3 * scale, 2)},
                {"shape": "box", "width": round(14 * scale, 2), "depth": round(0.5 * scale, 2), 
                 "height": round(0.3 * scale, 2), "x": 0, "y": 0, "z": round(2.5 * scale, 2)},
                {"shape": "pipe", "radius": round(0.6 * scale, 2), "length": round(10 * scale, 2), 
                 "x": round(-6 * scale, 2), "y": 0, "z": round(1 * scale, 2)}
            ]
        }
    
    elif "filter" in prompt_lower:
        print("🏭 Creating FILTER BANK")
        num_filters = extract_number_from_prompt(user_prompt, "filters", 4)
        num_filters = int(num_filters)
        
        components = []
        for i in range(num_filters):
            components.append({
                "shape": "box",
                "width": round(5 * scale, 2),
                "depth": round(5 * scale, 2),
                "height": round(4 * scale, 2),
                "x": round(i * 7 * scale, 2),
                "y": 0,
                "z": 0
            })
        
        params = {
            "type": "rapid_sand_filters",
            "description": f"Bank of {num_filters} rapid sand filters",
            "components": components,
            "piping": [
                {"shape": "pipe", "radius": round(1.0 * scale, 2), "length": round(num_filters * 7 * scale, 2),
                 "x": round((num_filters-1) * 3.5 * scale, 2), "y": round(3 * scale, 2), "z": round(2 * scale, 2)},
                {"shape": "pipe", "radius": round(1.0 * scale, 2), "length": round(num_filters * 7 * scale, 2),
                 "x": round((num_filters-1) * 3.5 * scale, 2), "y": round(-3 * scale, 2), "z": round(2 * scale, 2)}
            ]
        }
    
    elif "storage" in prompt_lower or "tank" in prompt_lower:
        print("🏭 Creating STORAGE TANK")
        params = {
            "type": "clear_water_reservoir",
            "description": "Clear water storage tank",
            "components": [
                {"shape": "cylinder", "radius": round(7 * scale, 2), "height": round(8 * scale, 2), 
                 "x": 0, "y": 0, "z": 0},
                {"shape": "cylinder", "radius": round(7.5 * scale, 2), "height": round(0.5 * scale, 2), 
                 "x": 0, "y": 0, "z": round(8 * scale, 2)},
                {"shape": "pipe", "radius": round(0.8 * scale, 2), "length": round(8 * scale, 2), 
                 "x": round(-5 * scale, 2), "y": 0, "z": round(4 * scale, 2)},
                {"shape": "pipe", "radius": round(0.8 * scale, 2), "length": round(8 * scale, 2), 
                 "x": round(5 * scale, 2), "y": 0, "z": round(4 * scale, 2)}
            ]
        }
    
    # ============== SIMPLE PLANT WITH EXPLICIT POSITIONS ==============
    elif any(x in prompt_lower for x in ["at x=", "position", "x="]):
        print("🏭 Creating PLANT WITH EXPLICIT POSITIONS")
        
        # Parse positions from prompt
        units = []
        
        # Look for cylinder patterns
        cylinder_matches = re.finditer(r'cylinder\s+r=(\d+(?:\.\d+)?)\s+h=(\d+(?:\.\d+)?)\s+at\s+x=(\d+(?:\.\d+)?)', prompt_lower)
        for match in cylinder_matches:
            units.append({
                "name": "Cylinder",
                "shape": "cylinder",
                "radius": float(match.group(1)),
                "height": float(match.group(2)),
                "x": float(match.group(3))
            })
        
        # Look for box patterns
        box_matches = re.finditer(r'box\s+w=(\d+(?:\.\d+)?)\s+d=(\d+(?:\.\d+)?)\s+h=(\d+(?:\.\d+)?)\s+at\s+x=(\d+(?:\.\d+)?)', prompt_lower)
        for match in box_matches:
            units.append({
                "name": "Box",
                "shape": "box",
                "width": float(match.group(1)),
                "depth": float(match.group(2)),
                "height": float(match.group(3)),
                "x": float(match.group(4))
            })
        
        # Sort units by x position
        units.sort(key=lambda u: u["x"])
        
        # Create connections between units
        connections = []
        for i in range(len(units)-1):
            connections.append({
                "from": i,
                "to": i+1,
                "radius": 1.2,
                "z": 3
            })
        
        params = {
            "type": "simple_wtp",
            "description": "Plant with explicit positions",
            "units": units,
            "connections": connections
        }
    
    # ============== DEFAULT = BASIC PLANT ==============
    else:
        print("🏭 Creating BASIC WATER TREATMENT PLANT")
        
        params = {
            "type": "simple_wtp",
            "description": f"Basic {mld} MLD water treatment plant",
            "capacity_mld": mld,
            "units": [
                {"name": "Intake", "shape": "cylinder", "radius": round(4 * scale, 2), 
                 "height": round(8 * scale, 2), "x": 0},
                {"name": "Clarifier", "shape": "cylinder", "radius": round(7 * scale, 2), 
                 "height": round(6 * scale, 2), "x": round(20 * scale, 2)},
                {"name": "Filter", "shape": "box", "width": round(6 * scale, 2), 
                 "depth": round(5 * scale, 2), "height": round(4 * scale, 2), 
                 "x": round(40 * scale, 2)},
                {"name": "Storage", "shape": "cylinder", "radius": round(6 * scale, 2), 
                 "height": round(7 * scale, 2), "x": round(60 * scale, 2)}
            ],
            "connections": [
                {"from": 0, "to": 1, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 1, "to": 2, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)},
                {"from": 2, "to": 3, "radius": round(1.0 * scale, 2), "z": round(3 * scale, 2)}
            ]
        }
    
    # Add metadata
    params["generated"] = datetime.now().isoformat()
    params["prompt"] = user_prompt
    
    # Convert to JSON
    json_str = json.dumps(params, indent=2)
    print(f"✅ Generated {params['type']} with {len(params.get('units', []))} units and {len(params.get('connections', []))} connections")
    
    return json_str

# Explicitly export the functions
__all__ = ['get_cad_code', 'extract_mld_from_prompt', 'extract_number_from_prompt']