#!/usr/bin/env python3
"""Generate WoT Thing Description from logistics ERDT model."""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with absolute imports
import models.industries.logistics as logistics
import transformation.erdt_to_wot as wot_transform

def main():
    # Create ERDT model
    print("Creating Logistics ERDT Model...")
    logistics_model = logistics.create_logistics_model()
    
    # Transform to WoT
    print("Transforming to WoT Thing Description...\n")
    wot_td = wot_transform.transform_erdt_to_wot(logistics_model)
    
    # Print formatted JSON
    print(json.dumps(wot_td, indent=2))
    
    # Also save to file
    with open('logistics_wot_td.json', 'w') as f:
        json.dump(wot_td, f, indent=2)
    print("\n✓ Saved to logistics_wot_td.json", file=sys.stderr)

if __name__ == "__main__":
    main()
