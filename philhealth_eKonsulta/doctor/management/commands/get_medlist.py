# (12/18/2025 - Gocotano) - Custom management command to populate Medicine table with Philippine medicines

from django.core.management.base import BaseCommand
from doctor.models import Medicine


class Command(BaseCommand):
    help = 'Populate the Medicine table with common Philippine medicines and their prices in PHP'

    # (12/18/2025 - Gocotano) - List of common Philippine medicines with prices
    PHILIPPINE_MEDICINES = [
        # Pain Relievers & Fever Reducers
        {"name": "Biogesic (Paracetamol 500mg)", "price": 5.50, "description": "For fever and mild pain relief"},
        {"name": "Medicol Advance (Ibuprofen 400mg)", "price": 12.00, "description": "For headache, muscle pain, and fever"},
        {"name": "Dolfenal (Mefenamic Acid 500mg)", "price": 8.75, "description": "For pain and inflammation"},
        {"name": "Advil (Ibuprofen 200mg)", "price": 15.00, "description": "Fast pain relief"},
        {"name": "Flanax (Naproxen 550mg)", "price": 18.50, "description": "For arthritis and muscle pain"},
        {"name": "Calpol (Paracetamol Suspension)", "price": 85.00, "description": "For children's fever"},
        {"name": "Tempra (Paracetamol Drops)", "price": 95.00, "description": "For infants fever"},

        # Cough & Cold
        {"name": "Bioflu (Phenylephrine + Chlorphenamine + Paracetamol)", "price": 12.00, "description": "For flu symptoms"},
        {"name": "Neozep (Phenylephrine + Chlorphenamine + Paracetamol)", "price": 8.50, "description": "For colds and flu"},
        {"name": "Decolgen (Phenylpropanolamine + Chlorphenamine + Paracetamol)", "price": 7.50, "description": "For nasal congestion and colds"},
        {"name": "Sinutab (Paracetamol + Phenylephrine)", "price": 14.00, "description": "For sinus congestion"},
        {"name": "Tuseran Forte (Dextromethorphan)", "price": 10.50, "description": "For dry cough"},
        {"name": "Solmux (Carbocisteine 500mg)", "price": 11.00, "description": "For productive cough with phlegm"},
        {"name": "Ascof Lagundi (Vitex negundo)", "price": 8.00, "description": "Herbal cough relief"},
        {"name": "Robitussin DM", "price": 145.00, "description": "Cough suppressant and expectorant"},
        {"name": "Benadryl (Diphenhydramine)", "price": 12.50, "description": "For allergies and cough"},

        # Antibiotics
        {"name": "Amoxicillin 500mg", "price": 15.00, "description": "Antibiotic for bacterial infections"},
        {"name": "Co-Amoxiclav 625mg", "price": 45.00, "description": "Broad-spectrum antibiotic"},
        {"name": "Cefalexin 500mg", "price": 25.00, "description": "Antibiotic for respiratory infections"},
        {"name": "Azithromycin 500mg", "price": 65.00, "description": "Antibiotic for respiratory and skin infections"},
        {"name": "Ciprofloxacin 500mg", "price": 18.00, "description": "Antibiotic for UTI and infections"},
        {"name": "Metronidazole 500mg", "price": 8.00, "description": "Antibiotic for anaerobic infections"},
        {"name": "Clindamycin 300mg", "price": 35.00, "description": "Antibiotic for serious infections"},
        {"name": "Doxycycline 100mg", "price": 12.00, "description": "Antibiotic for various infections"},

        # Gastrointestinal
        {"name": "Kremil-S (Aluminum/Magnesium Hydroxide + Simethicone)", "price": 8.00, "description": "For hyperacidity and gas pain"},
        {"name": "Gaviscon (Alginate)", "price": 22.00, "description": "For acid reflux and heartburn"},
        {"name": "Omeprazole 20mg", "price": 12.00, "description": "For ulcers and GERD"},
        {"name": "Ranitidine 150mg", "price": 8.50, "description": "For stomach acid reduction"},
        {"name": "Buscopan (Hyoscine 10mg)", "price": 18.00, "description": "For stomach cramps"},
        {"name": "Imodium (Loperamide 2mg)", "price": 25.00, "description": "For diarrhea"},
        {"name": "Diatabs (Loperamide 2mg)", "price": 12.00, "description": "For diarrhea"},
        {"name": "Dulcolax (Bisacodyl 5mg)", "price": 15.00, "description": "For constipation"},
        {"name": "Erceflora (Bacillus clausii)", "price": 45.00, "description": "Probiotic for gut health"},

        # Allergy & Antihistamines
        {"name": "Cetirizine 10mg", "price": 6.00, "description": "For allergies and allergic rhinitis"},
        {"name": "Loratadine 10mg", "price": 8.00, "description": "Non-drowsy antihistamine"},
        {"name": "Zyrtec (Cetirizine 10mg)", "price": 18.00, "description": "For allergic symptoms"},
        {"name": "Claritin (Loratadine 10mg)", "price": 22.00, "description": "Non-drowsy allergy relief"},
        {"name": "Chlorphenamine 4mg", "price": 3.50, "description": "For allergic reactions"},

        # Vitamins & Supplements
        {"name": "Enervon C (Multivitamins + Iron)", "price": 8.50, "description": "Daily multivitamin supplement"},
        {"name": "Centrum (Multivitamins)", "price": 25.00, "description": "Complete multivitamin"},
        {"name": "Vitamin C 500mg (Ascorbic Acid)", "price": 5.00, "description": "Immune system support"},
        {"name": "Berocca (B-Vitamins + C + Zinc)", "price": 28.00, "description": "Energy and immune support"},
        {"name": "Calcium + Vitamin D", "price": 12.00, "description": "For bone health"},
        {"name": "Fern-C (Sodium Ascorbate)", "price": 18.00, "description": "Non-acidic Vitamin C"},
        {"name": "Immunpro (Zinc + Vitamin C)", "price": 15.00, "description": "Immune booster"},
        {"name": "Conzace (Vitamins A, C, E + Zinc)", "price": 22.00, "description": "Antioxidant supplement"},

        # Cardiovascular & Blood Pressure
        {"name": "Amlodipine 5mg", "price": 8.00, "description": "For high blood pressure"},
        {"name": "Losartan 50mg", "price": 12.00, "description": "For hypertension"},
        {"name": "Metoprolol 50mg", "price": 10.00, "description": "Beta-blocker for heart"},
        {"name": "Atorvastatin 20mg", "price": 18.00, "description": "For cholesterol control"},
        {"name": "Simvastatin 20mg", "price": 15.00, "description": "For high cholesterol"},
        {"name": "Aspirin 80mg (Cardio)", "price": 5.00, "description": "Blood thinner for heart"},
        {"name": "Clopidogrel 75mg", "price": 25.00, "description": "Antiplatelet medication"},

        # Diabetes
        {"name": "Metformin 500mg", "price": 6.00, "description": "For Type 2 diabetes"},
        {"name": "Glimepiride 2mg", "price": 15.00, "description": "For blood sugar control"},
        {"name": "Gliclazide 80mg", "price": 12.00, "description": "For diabetes management"},

        # Respiratory & Asthma
        {"name": "Salbutamol 2mg", "price": 5.00, "description": "For asthma and bronchospasm"},
        {"name": "Ventolin Inhaler (Salbutamol)", "price": 450.00, "description": "Asthma rescue inhaler"},
        {"name": "Seretide Inhaler", "price": 1200.00, "description": "For asthma maintenance"},
        {"name": "Montelukast 10mg", "price": 35.00, "description": "For asthma prevention"},
        {"name": "Theophylline 200mg", "price": 8.00, "description": "For chronic bronchitis"},

        # Dermatological
        {"name": "Hydrocortisone Cream 1%", "price": 85.00, "description": "For skin inflammation and itching"},
        {"name": "Clotrimazole Cream 1%", "price": 75.00, "description": "Antifungal for skin infections"},
        {"name": "Mupirocin Ointment 2%", "price": 180.00, "description": "Antibiotic for skin infections"},
        {"name": "Betamethasone Cream", "price": 120.00, "description": "For severe skin inflammation"},
        {"name": "Ketoconazole Cream 2%", "price": 95.00, "description": "Antifungal cream"},

        # Eye & Ear
        {"name": "Visine (Tetrahydrozoline)", "price": 145.00, "description": "Eye drops for redness"},
        {"name": "Tobramycin Eye Drops", "price": 280.00, "description": "Antibiotic eye drops"},
        {"name": "Ciprofloxacin Eye Drops", "price": 220.00, "description": "For eye infections"},
        {"name": "Ear Drops (Otic Solution)", "price": 150.00, "description": "For ear infections"},

        # Muscle Relaxants
        {"name": "Orphenadrine 100mg", "price": 12.00, "description": "Muscle relaxant for spasms"},
        {"name": "Methocarbamol 500mg", "price": 15.00, "description": "For muscle pain and spasms"},
        {"name": "Baclofen 10mg", "price": 18.00, "description": "For muscle spasticity"},

        # Sleep & Anxiety
        {"name": "Sleepasil (Melatonin 3mg)", "price": 12.00, "description": "Natural sleep aid"},
        {"name": "Alprazolam 0.5mg", "price": 15.00, "description": "For anxiety (requires prescription)"},
        {"name": "Diazepam 5mg", "price": 12.00, "description": "For anxiety and muscle spasms"},

        # Women's Health
        {"name": "Mefenamic Acid 250mg (Ponstan)", "price": 10.00, "description": "For menstrual cramps"},
        {"name": "Tranexamic Acid 500mg", "price": 25.00, "description": "For heavy menstrual bleeding"},
        {"name": "Ferrous Sulfate 325mg", "price": 4.00, "description": "Iron supplement for anemia"},
        {"name": "Folic Acid 5mg", "price": 3.00, "description": "For pregnancy and anemia"},

        # Topical Pain Relief
        {"name": "Salonpas Patch", "price": 25.00, "description": "Topical pain relief patch"},
        {"name": "Efficascent Oil", "price": 45.00, "description": "For muscle and joint pain"},
        {"name": "Omega Pain Killer", "price": 35.00, "description": "Liniment for body aches"},
        {"name": "White Flower Oil", "price": 65.00, "description": "For headache and dizziness"},
        {"name": "Vicks VapoRub", "price": 85.00, "description": "For congestion and body aches"},
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting to populate Medicine table...'))

        created_count = 0
        updated_count = 0

        for med_data in self.PHILIPPINE_MEDICINES:
            # (12/18/2025 - Gocotano) - Use get_or_create to avoid duplicates
            medicine, created = Medicine.objects.get_or_create(
                name=med_data["name"],
                defaults={
                    "price": med_data["price"],
                    "description": med_data["description"],
                    "is_active": True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  + Added: {med_data["name"]} - ₱{med_data["price"]}')
            else:
                # (12/18/2025 - Gocotano) - Update existing medicine with new price if needed
                medicine.price = med_data["price"]
                medicine.description = med_data["description"]
                medicine.save()
                updated_count += 1
                self.stdout.write(f'  ~ Updated: {med_data["name"]} - ₱{med_data["price"]}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created: {created_count}, Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total medicines in database: {Medicine.objects.count()}'))
