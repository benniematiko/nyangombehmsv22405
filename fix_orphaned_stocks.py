# fix_orphaned_stocks.py
"""
Script to fix orphaned stock records that don't have a medicine linked.
Run with: python manage.py shell < fix_orphaned_stocks.py
"""

from pharmacy.models import Stock, Medicine

def fix_orphaned_stocks():
    """Find stock records without a medicine link and try to match them."""
    
    # Find orphaned stocks (medicine is None or blank)
    orphaned_stocks = Stock.objects.filter(medicine__isnull=True)
    
    if not orphaned_stocks.exists():
        print("✅ No orphaned stock records found. All stock items are properly linked!")
        return
    
    print(f"Found {orphaned_stocks.count()} orphaned stock records to fix...")
    print("-" * 50)
    
    fixed = 0
    skipped = 0
    not_found = 0
    
    for stock in orphaned_stocks:
        print(f"\nProcessing: '{stock.item_name}' (ID: {stock.id})")
        
        # Try to find a matching Medicine by exact name match first
        medicine = Medicine.objects.filter(name__iexact=stock.item_name).first()
        
        if medicine:
            stock.medicine = medicine
            stock.save(update_fields=['medicine'])
            fixed += 1
            print(f"  ✅ EXACT MATCH: '{stock.item_name}' → Medicine ID: {medicine.id}")
            continue
        
        # Try partial match using first 10 characters
        partial_name = stock.item_name[:10]
        medicine = Medicine.objects.filter(name__icontains=partial_name).first()
        
        if medicine:
            stock.medicine = medicine
            stock.save(update_fields=['medicine'])
            fixed += 1
            print(f"  ⚠️ PARTIAL MATCH: '{stock.item_name}' → '{medicine.name}' (ID: {medicine.id})")
            continue
        
        # Try matching by generic name if available
        if stock.generic_name:
            medicine = Medicine.objects.filter(generic_name__icontains=stock.generic_name[:10]).first()
            if medicine:
                stock.medicine = medicine
                stock.save(update_fields=['medicine'])
                fixed += 1
                print(f"  ⚠️ GENERIC MATCH: '{stock.item_name}' → '{medicine.name}' (ID: {medicine.id})")
                continue
        
        # No match found
        not_found += 1
        print(f"  ❌ NO MATCH FOUND: '{stock.item_name}'")
        print(f"     Please create a Medicine entry in Admin → Pharmacy → Medicines")
    
    print("\n" + "=" * 50)
    print(f"✅ Fixed: {fixed} stock records")
    print(f"❌ No match found: {not_found} stock records")
    print(f"⏭️  Skipped: {skipped} stock records")
    print("=" * 50)
    
    if not_found > 0:
        print("\n📝 For unmatched items, go to Admin → Pharmacy → Medicines and add the missing entries.")
        print("   Then run this script again to link them.")

if __name__ == "__main__":
    fix_orphaned_stocks()