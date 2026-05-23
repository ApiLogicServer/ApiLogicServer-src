"""
CBSA CLVS Program - Controlled, Regulated, and Prohibited Goods HS Codes
==========================================================================

Goods under these HS codes are NOT eligible for Courier Low Value Shipment (CLVS)
processing and require formal entry (B3 declaration) with applicable permits,
licences, or certificates from the relevant Other Government Department (OGD).

Reference: CBSA Memorandum D5-1-1, Customs Tariff Schedule, EIPA, CFIA, Health Canada
"""

CLVS_EXCLUDED_HS_CODES = {

    # =========================================================================
    # FIREARMS, WEAPONS & AMMUNITION (RCMP / Firearms Act)
    # =========================================================================
    "firearms_weapons": {
        "ogd": "RCMP / Canadian Firearms Program",
        "authority": "Firearms Act, Criminal Code Part III",
        "codes": [
            {"hs_code": "9301.10.00", "description": "Artillery weapons (e.g., guns, howitzers, mortars)", "clvs_reason": "Prohibited weapon"},
            {"hs_code": "9301.20.00", "description": "Rocket launchers, flame-throwers, grenade launchers", "clvs_reason": "Prohibited weapon"},
            {"hs_code": "9301.90.00", "description": "Other military weapons (excl. revolvers, pistols)", "clvs_reason": "Prohibited weapon"},
            {"hs_code": "9302.00.00", "description": "Revolvers and pistols (excl. those of 93.03/93.04)", "clvs_reason": "Restricted/prohibited firearm"},
            {"hs_code": "9303.10.00", "description": "Muzzle-loading firearms", "clvs_reason": "Firearm - requires PAL"},
            {"hs_code": "9303.20.00", "description": "Shotguns (sporting/hunting), incl. combination", "clvs_reason": "Firearm - requires PAL"},
            {"hs_code": "9303.30.00", "description": "Sporting/hunting rifles", "clvs_reason": "Firearm - requires PAL"},
            {"hs_code": "9303.90.00", "description": "Other firearms which operate by firing explosive charge", "clvs_reason": "Firearm - requires PAL"},
            {"hs_code": "9304.00.00", "description": "Air guns, spring guns, similar non-explosive weapons", "clvs_reason": "Regulated weapon"},
            {"hs_code": "9305.10.00", "description": "Parts and accessories for revolvers or pistols", "clvs_reason": "Firearm parts"},
            {"hs_code": "9305.20.00", "description": "Parts and accessories for shotguns or rifles", "clvs_reason": "Firearm parts"},
            {"hs_code": "9305.91.00", "description": "Parts and accessories for military weapons of 93.01", "clvs_reason": "Military weapon parts"},
            {"hs_code": "9305.99.00", "description": "Parts and accessories for other weapons of 93.03", "clvs_reason": "Weapon parts"},
            {"hs_code": "9306.21.00", "description": "Shotgun cartridges", "clvs_reason": "Ammunition"},
            {"hs_code": "9306.29.00", "description": "Parts of shotgun cartridges, air gun pellets", "clvs_reason": "Ammunition parts"},
            {"hs_code": "9306.30.00", "description": "Cartridges and parts thereof (excl. shotgun)", "clvs_reason": "Ammunition"},
            {"hs_code": "9306.90.00", "description": "Bombs, grenades, torpedoes, mines, missiles, similar", "clvs_reason": "Military munitions"},
        ]
    },

    # =========================================================================
    # ALCOHOL & EXCISE GOODS (CBSA Excise / CRA)
    # =========================================================================
    "alcohol_excise": {
        "ogd": "CBSA Excise / Canada Revenue Agency",
        "authority": "Excise Act, Excise Act 2001, Excise Tax Act",
        "codes": [
            {"hs_code": "2203.00.00", "description": "Beer made from malt", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2204.10.00", "description": "Sparkling wine", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2204.21.00", "description": "Wine in containers ≤2L (still)", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2204.22.00", "description": "Wine in containers >2L but ≤10L", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2204.29.00", "description": "Wine in containers >10L", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2205.10.00", "description": "Vermouth in containers ≤2L", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2205.90.00", "description": "Vermouth in containers >2L", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2206.00.00", "description": "Cider, perry, mead and other fermented beverages", "clvs_reason": "Excise good - alcohol"},
            {"hs_code": "2207.10.00", "description": "Undenatured ethyl alcohol ≥80% vol", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2207.20.00", "description": "Denatured ethyl alcohol and spirits", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.20.00", "description": "Spirits obtained from grape wine/marc (brandy)", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.30.00", "description": "Whiskies", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.40.00", "description": "Rum and other spirits from sugarcane", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.50.00", "description": "Gin and Geneva", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.60.00", "description": "Vodka", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.70.00", "description": "Liqueurs and cordials", "clvs_reason": "Excise good - spirits"},
            {"hs_code": "2208.90.00", "description": "Other spirits (tequila, sake, etc.)", "clvs_reason": "Excise good - spirits"},
        ]
    },

    # =========================================================================
    # TOBACCO PRODUCTS (CRA / Health Canada)
    # =========================================================================
    "tobacco": {
        "ogd": "Canada Revenue Agency / Health Canada",
        "authority": "Excise Act 2001, Tobacco and Vaping Products Act",
        "codes": [
            {"hs_code": "2401.10.00", "description": "Tobacco, not stemmed/stripped", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2401.20.00", "description": "Tobacco, partly or wholly stemmed/stripped", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2401.30.00", "description": "Tobacco refuse", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2402.10.00", "description": "Cigars, cheroots, cigarillos (containing tobacco)", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2402.20.00", "description": "Cigarettes containing tobacco", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2402.90.00", "description": "Other manufactured tobacco (hand-rolling, etc.)", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2403.11.00", "description": "Water pipe tobacco (shisha/hookah)", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2403.19.00", "description": "Other smoking tobacco", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2403.91.00", "description": "Homogenized or reconstituted tobacco", "clvs_reason": "Excise good - tobacco"},
            {"hs_code": "2403.99.00", "description": "Other manufactured tobacco (chewing, snuff)", "clvs_reason": "Excise good - tobacco"},
        ]
    },

    # =========================================================================
    # CANNABIS (Health Canada)
    # =========================================================================
    "cannabis": {
        "ogd": "Health Canada",
        "authority": "Cannabis Act (S.C. 2018, c.16)",
        "codes": [
            {"hs_code": "1211.90.00", "description": "Cannabis plants and parts (fresh or dried)", "clvs_reason": "Controlled substance - cannabis"},
            {"hs_code": "1302.19.00", "description": "Cannabis extracts and concentrates", "clvs_reason": "Controlled substance - cannabis"},
            {"hs_code": "2106.90.00", "description": "Cannabis edibles (food preparations containing cannabis)", "clvs_reason": "Controlled substance - cannabis"},
            {"hs_code": "3004.90.00", "description": "Cannabis-based medicaments (therapeutic)", "clvs_reason": "Controlled substance - cannabis"},
        ]
    },

    # =========================================================================
    # CONTROLLED SUBSTANCES & PRECURSOR CHEMICALS (Health Canada)
    # =========================================================================
    "controlled_substances": {
        "ogd": "Health Canada / Office of Controlled Substances",
        "authority": "Controlled Drugs and Substances Act (CDSA), Precursor Control Regulations",
        "codes": [
            {"hs_code": "2914.31.00", "description": "Phenylacetone (1-phenyl-2-propanone / P2P)", "clvs_reason": "Precursor chemical - Class A"},
            {"hs_code": "2921.11.00", "description": "Methylamine and salts", "clvs_reason": "Precursor chemical"},
            {"hs_code": "2921.19.00", "description": "Other acyclic monoamines (incl. amphetamine precursors)", "clvs_reason": "Precursor chemical"},
            {"hs_code": "2922.19.00", "description": "Ephedrine and pseudoephedrine (amino-alcohols)", "clvs_reason": "Precursor chemical - Schedule V CDSA"},
            {"hs_code": "2924.29.00", "description": "Cyclic amides (incl. fentanyl precursors)", "clvs_reason": "Precursor chemical"},
            {"hs_code": "2932.91.00", "description": "Isosafrole", "clvs_reason": "Precursor chemical - Class A"},
            {"hs_code": "2932.92.00", "description": "1-(1,3-Benzodioxol-5-yl)propan-2-one", "clvs_reason": "Precursor chemical - Class A"},
            {"hs_code": "2932.93.00", "description": "Piperonal", "clvs_reason": "Precursor chemical - Class A"},
            {"hs_code": "2932.94.00", "description": "Safrole", "clvs_reason": "Precursor chemical - Class A"},
            {"hs_code": "2933.32.00", "description": "Piperidine and its salts", "clvs_reason": "Precursor chemical"},
            {"hs_code": "2939.11.00", "description": "Concentrates of poppy straw (opium alkaloids)", "clvs_reason": "Narcotic - Schedule I CDSA"},
            {"hs_code": "2939.19.00", "description": "Other alkaloids of opium (codeine, morphine)", "clvs_reason": "Narcotic - Schedule I CDSA"},
            {"hs_code": "2939.41.00", "description": "Ephedrine and its salts", "clvs_reason": "Precursor - Schedule V CDSA"},
            {"hs_code": "2939.42.00", "description": "Pseudoephedrine and its salts", "clvs_reason": "Precursor - Schedule V CDSA"},
            {"hs_code": "2939.49.00", "description": "Other ephedrines (norephedrine etc.)", "clvs_reason": "Precursor - Schedule V CDSA"},
            {"hs_code": "2939.71.00", "description": "Cocaine, ecgonine and derivatives", "clvs_reason": "Narcotic - Schedule I CDSA"},
            {"hs_code": "2939.79.00", "description": "Other alkaloids of coca (incl. crude cocaine)", "clvs_reason": "Narcotic - Schedule I CDSA"},
            {"hs_code": "2934.91.00", "description": "GHB and analogues (aminorex, brotizolam etc.)", "clvs_reason": "Controlled substance - Schedule III/IV CDSA"},
            {"hs_code": "2933.33.00", "description": "Alfentanil, fentanyl, sufentanil and salts", "clvs_reason": "Narcotic - Schedule I CDSA"},
        ]
    },

    # =========================================================================
    # PHARMACEUTICALS & HEALTH PRODUCTS (Health Canada)
    # =========================================================================
    "pharmaceuticals": {
        "ogd": "Health Canada / Therapeutic Products Directorate",
        "authority": "Food and Drugs Act, Medical Devices Regulations",
        "codes": [
            {"hs_code": "3001.20.00", "description": "Extracts of glands or organs (human/animal)", "clvs_reason": "Regulated health product"},
            {"hs_code": "3002.12.00", "description": "Antisera and other blood fractions", "clvs_reason": "Biologic - requires DIN"},
            {"hs_code": "3002.13.00", "description": "Immunological products (vaccines)", "clvs_reason": "Biologic - requires DIN"},
            {"hs_code": "3002.14.00", "description": "Immunological products for veterinary use", "clvs_reason": "Vet biologic - CFIA regulated"},
            {"hs_code": "3002.15.00", "description": "Immunological products for human use", "clvs_reason": "Biologic - requires DIN"},
            {"hs_code": "3003.10.00", "description": "Medicaments containing penicillins (bulk)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3003.20.00", "description": "Medicaments containing antibiotics (bulk)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3003.41.00", "description": "Medicaments containing alkaloids (bulk)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3004.10.00", "description": "Medicaments containing penicillins (dosage form)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3004.20.00", "description": "Medicaments containing antibiotics (dosage form)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3004.41.00", "description": "Medicaments containing ephedrine (dosage form)", "clvs_reason": "Controlled - CDSA listed"},
            {"hs_code": "3004.49.00", "description": "Medicaments containing alkaloids (dosage form)", "clvs_reason": "Prescription drug - requires DIN"},
            {"hs_code": "3004.50.00", "description": "Vitamins in therapeutic doses (as medicaments)", "clvs_reason": "NHP - requires NPN"},
            {"hs_code": "3006.30.00", "description": "Opacifying preparations for X-ray examinations", "clvs_reason": "Regulated medical device"},
            {"hs_code": "3006.91.00", "description": "Ostomy appliances", "clvs_reason": "Medical device - Class II+"},
            {"hs_code": "9018.11.00", "description": "Electrocardiographs", "clvs_reason": "Medical device - Class III"},
            {"hs_code": "9018.12.00", "description": "Ultrasonic scanning apparatus", "clvs_reason": "Medical device - Class III"},
            {"hs_code": "9018.13.00", "description": "MRI apparatus", "clvs_reason": "Medical device - Class III"},
            {"hs_code": "9018.14.00", "description": "Scintigraphic apparatus", "clvs_reason": "Medical device - Class III"},
            {"hs_code": "9018.31.00", "description": "Syringes (with or without needles)", "clvs_reason": "Medical device - Class II"},
            {"hs_code": "9018.39.00", "description": "Catheters, cannulae and the like", "clvs_reason": "Medical device - Class II+"},
            {"hs_code": "9021.10.00", "description": "Orthopaedic or fracture appliances", "clvs_reason": "Medical device - Class II+"},
            {"hs_code": "9021.21.00", "description": "Artificial teeth", "clvs_reason": "Medical device - Class II"},
            {"hs_code": "9021.31.00", "description": "Artificial joints", "clvs_reason": "Medical device - Class III"},
            {"hs_code": "9021.40.00", "description": "Hearing aids", "clvs_reason": "Medical device - Class II"},
            {"hs_code": "9021.50.00", "description": "Pacemakers for stimulating heart muscles", "clvs_reason": "Medical device - Class IV"},
        ]
    },

    # =========================================================================
    # FOOD, PLANT & ANIMAL PRODUCTS (CFIA)
    # =========================================================================
    "food_plant_animal": {
        "ogd": "Canadian Food Inspection Agency (CFIA)",
        "authority": "Safe Food for Canadians Act, Health of Animals Act, Plant Protection Act",
        "codes": [
            # Meat & Animal Products
            {"hs_code": "0201.10.00", "description": "Carcasses of bovine animals, fresh/chilled", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0201.20.00", "description": "Cuts of bovine, bone-in, fresh/chilled", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0201.30.00", "description": "Boneless bovine meat, fresh/chilled", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0202.10.00", "description": "Carcasses of bovine animals, frozen", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0203.11.00", "description": "Carcasses of swine, fresh/chilled", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0203.21.00", "description": "Carcasses of swine, frozen", "clvs_reason": "CFIA inspection required - meat"},
            {"hs_code": "0207.11.00", "description": "Poultry (chicken), not cut, fresh/chilled", "clvs_reason": "CFIA inspection required - poultry"},
            {"hs_code": "0207.14.00", "description": "Poultry (chicken), cuts and offal, frozen", "clvs_reason": "CFIA inspection required - poultry"},
            {"hs_code": "0210.11.00", "description": "Hams, shoulders of swine, salted/dried/smoked", "clvs_reason": "CFIA inspection required - processed meat"},
            {"hs_code": "0210.19.00", "description": "Other meat of swine, salted/dried/smoked", "clvs_reason": "CFIA inspection required - processed meat"},
            {"hs_code": "1601.00.00", "description": "Sausages and similar products of meat", "clvs_reason": "CFIA inspection required - processed meat"},
            {"hs_code": "1602.10.00", "description": "Homogenized prepared meat", "clvs_reason": "CFIA inspection required - processed meat"},

            # Dairy
            {"hs_code": "0401.10.00", "description": "Milk and cream, not concentrated, ≤1% fat", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0401.20.00", "description": "Milk and cream, not concentrated, 1-6% fat", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0401.40.00", "description": "Milk and cream, not concentrated, >6% fat", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0402.10.00", "description": "Milk powder, ≤1.5% fat", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0403.10.00", "description": "Yogurt", "clvs_reason": "CFIA inspection - dairy"},
            {"hs_code": "0406.10.00", "description": "Fresh cheese (unripened), incl. curd", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0406.90.00", "description": "Other cheese", "clvs_reason": "CFIA inspection - dairy / supply managed"},
            {"hs_code": "0407.11.00", "description": "Fertilized eggs for incubation (chicken)", "clvs_reason": "CFIA inspection - poultry / supply managed"},
            {"hs_code": "0407.21.00", "description": "Fresh eggs, in shell (chicken)", "clvs_reason": "CFIA inspection - eggs / supply managed"},

            # Fish & Seafood
            {"hs_code": "0302.11.00", "description": "Trout, fresh or chilled", "clvs_reason": "CFIA inspection required - fish"},
            {"hs_code": "0302.14.00", "description": "Atlantic and Danube salmon, fresh/chilled", "clvs_reason": "CFIA inspection required - fish"},
            {"hs_code": "0303.11.00", "description": "Sockeye salmon, frozen", "clvs_reason": "CFIA inspection required - fish"},
            {"hs_code": "0306.11.00", "description": "Frozen rock lobster and other sea crawfish", "clvs_reason": "CFIA inspection required - crustaceans"},

            # Plants, Seeds, Soil
            {"hs_code": "0601.10.00", "description": "Bulbs, tubers, roots (dormant)", "clvs_reason": "CFIA phytosanitary inspection"},
            {"hs_code": "0601.20.00", "description": "Bulbs, tubers, roots (in growth/flower)", "clvs_reason": "CFIA phytosanitary inspection"},
            {"hs_code": "0602.10.00", "description": "Unrooted cuttings and slips", "clvs_reason": "CFIA phytosanitary inspection"},
            {"hs_code": "0602.20.00", "description": "Trees, shrubs, bushes (edible fruit/nut)", "clvs_reason": "CFIA phytosanitary inspection"},
            {"hs_code": "0602.90.00", "description": "Other live plants (incl. roots)", "clvs_reason": "CFIA phytosanitary inspection"},
            {"hs_code": "1209.10.00", "description": "Sugar beet seeds", "clvs_reason": "CFIA - Seeds Act inspection"},
            {"hs_code": "1209.91.00", "description": "Vegetable seeds", "clvs_reason": "CFIA - Seeds Act inspection"},
            {"hs_code": "2530.90.00", "description": "Soil, earth, and growing media", "clvs_reason": "CFIA - prohibited (pest/pathogen risk)"},

            # Live Animals
            {"hs_code": "0101.21.00", "description": "Live horses (pure-bred breeding)", "clvs_reason": "CFIA Health of Animals inspection"},
            {"hs_code": "0102.21.00", "description": "Live bovine (pure-bred breeding)", "clvs_reason": "CFIA Health of Animals inspection"},
            {"hs_code": "0105.11.00", "description": "Live chickens ≤185g", "clvs_reason": "CFIA Health of Animals inspection"},
            {"hs_code": "0106.11.00", "description": "Live primates", "clvs_reason": "CFIA + CITES regulated"},
            {"hs_code": "0106.19.00", "description": "Other live mammals", "clvs_reason": "CFIA Health of Animals inspection"},
        ]
    },

    # =========================================================================
    # ENDANGERED SPECIES / CITES (Environment Canada)
    # =========================================================================
    "cites_wildlife": {
        "ogd": "Environment and Climate Change Canada",
        "authority": "Wild Animal and Plant Protection Act (WAPPRIITA), CITES",
        "codes": [
            {"hs_code": "0507.10.00", "description": "Ivory, unworked or simply prepared", "clvs_reason": "CITES Appendix I - prohibited"},
            {"hs_code": "0507.90.00", "description": "Tortoiseshell, whalebone, horns, antlers", "clvs_reason": "CITES regulated - permit required"},
            {"hs_code": "0508.00.00", "description": "Coral and similar materials", "clvs_reason": "CITES Appendix II - permit required"},
            {"hs_code": "4103.30.00", "description": "Reptile hides (raw)", "clvs_reason": "CITES regulated - permit required"},
            {"hs_code": "4301.10.00", "description": "Mink furskins, raw (whole)", "clvs_reason": "May require CITES permit"},
            {"hs_code": "4301.60.00", "description": "Fox furskins, raw (whole)", "clvs_reason": "May require CITES permit"},
            {"hs_code": "4301.80.00", "description": "Other furskins, raw (whole)", "clvs_reason": "CITES regulated species possible"},
            {"hs_code": "0511.91.00", "description": "Products of fish (caviar - sturgeon)", "clvs_reason": "CITES Appendix II - sturgeon caviar"},
            {"hs_code": "1211.90.00", "description": "Plants for pharmacy (incl. CITES flora)", "clvs_reason": "CITES regulated flora possible"},
            {"hs_code": "9601.10.00", "description": "Worked ivory and articles of ivory", "clvs_reason": "CITES Appendix I - prohibited"},
            {"hs_code": "9601.90.00", "description": "Carved bone, shell, horn (CITES species)", "clvs_reason": "CITES regulated - permit required"},
        ]
    },

    # =========================================================================
    # EXPLOSIVES & HAZARDOUS MATERIALS (NRCan / Transport Canada)
    # =========================================================================
    "explosives_hazmat": {
        "ogd": "Natural Resources Canada / Transport Canada",
        "authority": "Explosives Act, Transportation of Dangerous Goods Act",
        "codes": [
            {"hs_code": "2804.70.00", "description": "Phosphorus (white/yellow)", "clvs_reason": "Prohibited import - white phosphorus"},
            {"hs_code": "3601.00.00", "description": "Propellent powders", "clvs_reason": "Explosive - NRCan permit required"},
            {"hs_code": "3602.00.00", "description": "Prepared explosives (other than propellent)", "clvs_reason": "Explosive - NRCan permit required"},
            {"hs_code": "3603.00.00", "description": "Detonating fuses, detonators, igniters", "clvs_reason": "Explosive - NRCan permit required"},
            {"hs_code": "3604.10.00", "description": "Fireworks", "clvs_reason": "Explosive - NRCan permit required"},
            {"hs_code": "3604.90.00", "description": "Signalling flares, rain rockets, fog signals", "clvs_reason": "Explosive - NRCan permit required"},
            {"hs_code": "2844.10.00", "description": "Natural uranium and compounds", "clvs_reason": "Nuclear material - CNSC licence required"},
            {"hs_code": "2844.20.00", "description": "Enriched uranium and plutonium", "clvs_reason": "Nuclear material - CNSC licence required"},
            {"hs_code": "2844.30.00", "description": "Depleted uranium and thorium", "clvs_reason": "Nuclear material - CNSC licence required"},
            {"hs_code": "2844.40.00", "description": "Radioactive elements/isotopes (not 2844.10-30)", "clvs_reason": "Radioactive material - CNSC licence"},
            {"hs_code": "2612.10.00", "description": "Uranium ores and concentrates", "clvs_reason": "Nuclear material - CNSC licence required"},
        ]
    },

    # =========================================================================
    # STRATEGIC / DUAL-USE / MILITARY GOODS (Global Affairs Canada)
    # =========================================================================
    "strategic_military": {
        "ogd": "Global Affairs Canada / Export & Import Controls Bureau",
        "authority": "Export and Import Permits Act (EIPA), Defence Production Act",
        "codes": [
            {"hs_code": "8401.10.00", "description": "Nuclear reactors", "clvs_reason": "Strategic good - EIPA permit"},
            {"hs_code": "8401.20.00", "description": "Machinery for isotopic separation", "clvs_reason": "Strategic good - EIPA permit"},
            {"hs_code": "8401.40.00", "description": "Parts of nuclear reactors", "clvs_reason": "Strategic good - EIPA permit"},
            {"hs_code": "8526.10.00", "description": "Radar apparatus", "clvs_reason": "Dual-use technology"},
            {"hs_code": "8543.70.00", "description": "Other electrical machines (incl. signal jammers)", "clvs_reason": "Dual-use technology possible"},
            {"hs_code": "9005.10.00", "description": "Binoculars (military-grade night vision)", "clvs_reason": "Dual-use - night vision controlled"},
            {"hs_code": "9013.10.00", "description": "Telescopic sights, periscopes (weapon sights)", "clvs_reason": "Dual-use military optic"},
            {"hs_code": "8710.00.00", "description": "Tanks and other armoured fighting vehicles", "clvs_reason": "Military equipment - EIPA"},
            {"hs_code": "8802.11.00", "description": "Helicopters ≤2000 kg (incl. military)", "clvs_reason": "Controlled aircraft"},
            {"hs_code": "8906.10.00", "description": "Warships", "clvs_reason": "Military equipment - EIPA"},
        ]
    },

    # =========================================================================
    # CULTURAL PROPERTY & HERITAGE (Canadian Heritage)
    # =========================================================================
    "cultural_property": {
        "ogd": "Canadian Heritage / Canadian Cultural Property Export Review Board",
        "authority": "Cultural Property Export and Import Act",
        "codes": [
            {"hs_code": "9701.10.00", "description": "Paintings, drawings (original, by hand)", "clvs_reason": "Cultural property assessment may apply"},
            {"hs_code": "9702.00.00", "description": "Original engravings, prints, lithographs", "clvs_reason": "Cultural property assessment may apply"},
            {"hs_code": "9703.00.00", "description": "Original sculptures and statuary", "clvs_reason": "Cultural property assessment may apply"},
            {"hs_code": "9704.00.00", "description": "Postage stamps, revenue stamps (collector's)", "clvs_reason": "Cultural property if >100 yrs old"},
            {"hs_code": "9705.00.00", "description": "Numismatic coins (collector's)", "clvs_reason": "Cultural property if >100 yrs old"},
            {"hs_code": "9706.00.00", "description": "Antiques of age exceeding 100 years", "clvs_reason": "Cultural property - export cert required"},
        ]
    },

    # =========================================================================
    # TEXTILE QUOTA / IMPORT PERMIT GOODS (Global Affairs)
    # =========================================================================
    "textile_quota": {
        "ogd": "Global Affairs Canada",
        "authority": "Export and Import Permits Act (EIPA), Import Control List",
        "codes": [
            {"hs_code": "5208.11.00", "description": "Woven cotton fabrics ≤200g/m², unbleached, plain", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "5209.11.00", "description": "Woven cotton fabrics >200g/m², unbleached, plain", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "5407.10.00", "description": "Woven fabrics of high-tenacity nylon yarn", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "5515.11.00", "description": "Woven fabrics of polyester staple fibres", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "6110.20.00", "description": "Jerseys, pullovers, cardigans (cotton)", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "6203.42.00", "description": "Men's trousers, shorts (cotton)", "clvs_reason": "Textile - may require import permit"},
            {"hs_code": "6204.62.00", "description": "Women's trousers, shorts (cotton)", "clvs_reason": "Textile - may require import permit"},
        ]
    },

    # =========================================================================
    # PEST CONTROL / CONSUMER PRODUCTS (Health Canada / PMRA)
    # =========================================================================
    "pest_control_consumer": {
        "ogd": "Health Canada / Pest Management Regulatory Agency",
        "authority": "Pest Control Products Act, Canada Consumer Product Safety Act",
        "codes": [
            {"hs_code": "3808.50.00", "description": "Goods specified in Sub-Note 1 to Ch. 38 (hazardous)", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "3808.91.00", "description": "Insecticides", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "3808.92.00", "description": "Fungicides", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "3808.93.00", "description": "Herbicides, anti-sprouting, plant growth regulators", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "3808.94.00", "description": "Disinfectants", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "3808.99.00", "description": "Other pesticides (rodenticides, etc.)", "clvs_reason": "Pesticide - PMRA registration required"},
            {"hs_code": "9613.10.00", "description": "Pocket lighters, gas-fuelled (non-refillable)", "clvs_reason": "Consumer safety - CCPSA regulated"},
            {"hs_code": "3605.00.00", "description": "Matches", "clvs_reason": "Hazardous consumer product - CCPSA"},
        ]
    },
}


def get_all_excluded_hs_codes():
    """Return flat list of all HS codes excluded from CLVS"""
    codes = []
    for category, data in CLVS_EXCLUDED_HS_CODES.items():
        for item in data["codes"]:
            codes.append({
                "hs_code": item["hs_code"],
                "description": item["description"],
                "category": category,
                "ogd": data["ogd"],
                "authority": data["authority"],
                "clvs_reason": item["clvs_reason"],
            })
    return codes


def is_clvs_excluded(hs_code: str) -> dict | None:
    """
    Check if an HS code is excluded from CLVS processing.
    Returns exclusion details dict if excluded, None if eligible.
    """
    for category, data in CLVS_EXCLUDED_HS_CODES.items():
        for item in data["codes"]:
            if item["hs_code"] == hs_code:
                return {
                    "hs_code": hs_code,
                    "description": item["description"],
                    "category": category,
                    "ogd": data["ogd"],
                    "authority": data["authority"],
                    "clvs_reason": item["clvs_reason"],
                    "excluded": True,
                }
    return None


def get_category_summary():
    """Return summary count of excluded HS codes by category"""
    summary = {}
    for category, data in CLVS_EXCLUDED_HS_CODES.items():
        summary[category] = {
            "ogd": data["ogd"],
            "authority": data["authority"],
            "count": len(data["codes"]),
        }
    return summary


if __name__ == "__main__":
    print("CBSA CLVS Program - Controlled/Regulated HS Codes Summary")
    print("=" * 65)
    total = 0
    for category, info in get_category_summary().items():
        print(f"\n  {category:<30} {info['count']:>3} codes  ({info['ogd']})")
        total += info["count"]
    print(f"\n{'Total excluded HS codes:':<33} {total}")
    print("\nUse is_clvs_excluded('XXXX.XX.XX') to check a specific code.")
