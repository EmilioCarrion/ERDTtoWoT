"""Test to generate and save WoT TDs."""
import json
import pytest

def test_generate_logistics_wot_tds(logistics_model):
    """Generate WoT TDs from logistics model and save to files."""
    from ..transformation.erdt_to_wot import transform_erdt_to_wot
    
    # Transform - now returns dict of TDs (one per entity)
    wot_tds = transform_erdt_to_wot(logistics_model)
    
    print(f"\n✓ Generated {len(wot_tds)} WoT Thing Descriptions (one per entity)")
    
    # Save each entity's TD to a separate file
    for entity_name, wot_td in wot_tds.items():
        output_file = f'logistics_{entity_name.lower()}_td.json'
        with open(output_file, 'w') as f:
            json.dump(wot_td, f, indent=2)
        
        print(f"\n{entity_name} Thing Description:")
        print(f"  - {len(wot_td.get('properties', {}))} properties")
        print(f"  - {len(wot_td.get('actions', {}))} actions")
        print(f"  - {len(wot_td.get('events', {}))} events")
        print(f"  - {len(wot_td.get('links', []))} links to other Things")
        print(f"  ✓ Saved to: {output_file}")
    
    # Also print one example (Picker)
    if "Picker" in wot_tds:
        print("\n" + "="*80)
        print("EXAMPLE: Picker Thing Description")
        print("="*80)
        print(json.dumps(wot_tds["Picker"], indent=2))
    
    assert wot_tds is not None
    assert len(wot_tds) == 4  # Hive, Picker, Truck, Driver
