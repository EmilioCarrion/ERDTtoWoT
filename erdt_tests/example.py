"""
Example: Using the ERDT framework to create and transform a digital twin model.

This example demonstrates:
1. Creating an ERDT model using the logistics case study
2. Transforming it to WoT Thing Description
3. Validating the WoT TD
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from models.industries.logistics import create_logistics_model
from transformation.erdt_to_wot import transform_erdt_to_wot
from validation.wot_validator import validate_wot_thing_description
import json


def main():
    print("=" * 80)
    print("ERDT Framework Example - Logistics Digital Twin")
    print("=" * 80)
    
    # Step 1: Create ERDT model
    print("\n1. Creating Logistics ERDT Model...")
    logistics_model = create_logistics_model()
    print(logistics_model.summary())
    
    # Step 2: Transform to WoT
    print("\n2. Transforming ERDT to WoT Thing Description...")
    wot_td = transform_erdt_to_wot(logistics_model)
    print(f"   Generated WoT TD with:")
    print(f"   - {len(wot_td.get('properties', {}))} properties")
    print(f"   - {len(wot_td.get('actions', {}))} actions")
    print(f"   - {len(wot_td.get('events', {}))} events")
    
    # Step 3: Validate WoT TD
    print("\n3. Validating WoT Thing Description...")
    is_valid, messages = validate_wot_thing_description(wot_td)
    print(f"   Valid: {is_valid}")
    if messages:
        print("   Messages:")
        for msg in messages:
            print(f"   - {msg}")
    
    # Step 4: Show sample WoT TD structure
    print("\n4. Sample WoT Thing Description Structure:")
    print("-" * 80)
    
    # Show a few properties
    print("\nSample Properties:")
    for i, (prop_name, prop_def) in enumerate(list(wot_td['properties'].items())[:3]):
        print(f"  {prop_name}:")
        print(f"    type: {prop_def.get('type')}")
        print(f"    observable: {prop_def.get('observable', False)}")
        print(f"    readOnly: {prop_def.get('readOnly', True)}")
    
    # Show a few actions
    print("\nSample Actions:")
    for i, (action_name, action_def) in enumerate(list(wot_td['actions'].items())[:3]):
        print(f"  {action_name}:")
        print(f"    description: {action_def.get('description', 'N/A')[:60]}...")
    
    # Show events
    print("\nEvents:")
    for event_name, event_def in wot_td['events'].items():
        print(f"  {event_name}:")
        print(f"    description: {event_def.get('description', 'N/A')[:60]}...")
    
    # Step 5: Save WoT TD to file
    output_file = "logistics_wot_td.json"
    with open(output_file, 'w') as f:
        json.dump(wot_td, f, indent=2)
    print(f"\n5. WoT Thing Description saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
