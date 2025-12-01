"""Test to generate and save WoT TD."""
import json
import pytest

def test_generate_logistics_wot_td(logistics_model):
    """Generate WoT TD from logistics model and save to file."""
    from ..transformation.erdt_to_wot import transform_erdt_to_wot
    
    # Transform
    wot_td = transform_erdt_to_wot(logistics_model)
    
    # Save to file
    output_file = 'logistics_wot_td.json'
    with open(output_file, 'w') as f:
        json.dump(wot_td, f, indent=2)
    
    print(f"\n✓ WoT Thing Description saved to: {output_file}")
    print(f"\nGenerated WoT TD with:")
    print(f"  - {len(wot_td.get('properties', {}))} properties")
    print(f"  - {len(wot_td.get('actions', {}))} actions")
    print(f"  - {len(wot_td.get('events', {}))} events")
    
    # Also print it
    print("\n" + "="*80)
    print("WoT THING DESCRIPTION:")
    print("="*80)
    print(json.dumps(wot_td, indent=2))
    
    assert wot_td is not None
