"""
CBSA Designated Customs Offices - Office Codes and Locations
=============================================================

Reference data for all CBSA customs offices where goods may be reported,
released, and accounted for under the Customs Act and CLVS program.

Each office has a 4-digit CBSA office code, region, and operational details.

Reference: CBSA Memorandum D1-1-1, List of Customs Offices (CBSA website)
"""

CBSA_CUSTOMS_OFFICES = {

    # =========================================================================
    # ATLANTIC REGION
    # =========================================================================
    "atlantic": {
        "region_name": "Atlantic Region",
        "regional_hq": "Moncton, NB",
        "offices": [
            # New Brunswick
            {"office_code": "0404", "name": "Saint John Airport", "province": "NB", "city": "Saint John", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0408", "name": "Saint John Seaport", "province": "NB", "city": "Saint John", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0453", "name": "Moncton Airport (Greater Moncton)", "province": "NB", "city": "Moncton", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0427", "name": "Woodstock", "province": "NB", "city": "Woodstock", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0415", "name": "St. Stephen", "province": "NB", "city": "St. Stephen", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0459", "name": "Edmundston", "province": "NB", "city": "Edmundston", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0469", "name": "Campbellton", "province": "NB", "city": "Campbellton", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},

            # Nova Scotia
            {"office_code": "0304", "name": "Halifax Stanfield International Airport", "province": "NS", "city": "Halifax", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0308", "name": "Halifax Seaport (Fairview Cove / South End)", "province": "NS", "city": "Halifax", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0355", "name": "Sydney", "province": "NS", "city": "Sydney", "type": "Marine", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "0340", "name": "Yarmouth", "province": "NS", "city": "Yarmouth", "type": "Marine", "clvs_release": False, "sufferance_warehouse": False},

            # Prince Edward Island
            {"office_code": "0204", "name": "Charlottetown", "province": "PE", "city": "Charlottetown", "type": "Airport/Marine", "clvs_release": True, "sufferance_warehouse": False},

            # Newfoundland and Labrador
            {"office_code": "0104", "name": "St. John's International Airport", "province": "NL", "city": "St. John's", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0108", "name": "St. John's Seaport", "province": "NL", "city": "St. John's", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0143", "name": "Corner Brook", "province": "NL", "city": "Corner Brook", "type": "Marine", "clvs_release": False, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # QUEBEC REGION
    # =========================================================================
    "quebec": {
        "region_name": "Quebec Region",
        "regional_hq": "Montreal, QC",
        "offices": [
            # Montreal Area
            {"office_code": "0500", "name": "Montréal-Trudeau International Airport", "province": "QC", "city": "Dorval", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0504", "name": "Montréal Mirabel Airport (Cargo)", "province": "QC", "city": "Mirabel", "type": "Airport/Cargo", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0508", "name": "Port of Montréal", "province": "QC", "city": "Montréal", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0510", "name": "Montréal Postal Facility", "province": "QC", "city": "Montréal", "type": "Postal/Courier", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0536", "name": "Montréal Courier Facility (Lachine)", "province": "QC", "city": "Lachine", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},

            # Quebec City Area
            {"office_code": "0560", "name": "Québec Jean Lesage International Airport", "province": "QC", "city": "Québec City", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0564", "name": "Port of Québec", "province": "QC", "city": "Québec City", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},

            # Land Borders
            {"office_code": "0580", "name": "Lacolle (Rte 15 / I-87)", "province": "QC", "city": "Lacolle", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0584", "name": "Stanstead (Rte 55 / I-91)", "province": "QC", "city": "Stanstead", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0586", "name": "Saint-Armand / Philipsburg", "province": "QC", "city": "Saint-Armand", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0590", "name": "Rock Island", "province": "QC", "city": "Rock Island", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "0594", "name": "Trout River / Dundee", "province": "QC", "city": "Dundee", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},

            # Other
            {"office_code": "0574", "name": "Trois-Rivières", "province": "QC", "city": "Trois-Rivières", "type": "Marine", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "0568", "name": "Port of Bécancour", "province": "QC", "city": "Bécancour", "type": "Marine", "clvs_release": False, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # NORTHERN ONTARIO REGION
    # =========================================================================
    "northern_ontario": {
        "region_name": "Northern Ontario Region",
        "regional_hq": "Hamilton, ON",
        "offices": [
            {"office_code": "0614", "name": "Ottawa Macdonald-Cartier International Airport", "province": "ON", "city": "Ottawa", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0618", "name": "Ottawa Postal Facility", "province": "ON", "city": "Ottawa", "type": "Postal/Courier", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0630", "name": "Prescott (Ogdensburg-Prescott Bridge)", "province": "ON", "city": "Prescott", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0634", "name": "Lansdowne (Thousand Islands Bridge)", "province": "ON", "city": "Lansdowne", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0642", "name": "Cornwall", "province": "ON", "city": "Cornwall", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0680", "name": "Sault Ste. Marie International Bridge", "province": "ON", "city": "Sault Ste. Marie", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0690", "name": "Thunder Bay", "province": "ON", "city": "Thunder Bay", "type": "Airport/Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0694", "name": "Fort Frances", "province": "ON", "city": "Fort Frances", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0660", "name": "Sudbury", "province": "ON", "city": "Sudbury", "type": "Inland", "clvs_release": False, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # GREATER TORONTO AREA (GTA) REGION
    # =========================================================================
    "gta": {
        "region_name": "Greater Toronto Area Region",
        "regional_hq": "Toronto, ON",
        "offices": [
            {"office_code": "0700", "name": "Toronto Pearson International Airport - Terminal 1", "province": "ON", "city": "Mississauga", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0701", "name": "Toronto Pearson International Airport - Terminal 3", "province": "ON", "city": "Mississauga", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0704", "name": "Toronto Pearson Cargo (Infield)", "province": "ON", "city": "Mississauga", "type": "Airport/Cargo", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0708", "name": "Port of Toronto (Marine Terminal)", "province": "ON", "city": "Toronto", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0712", "name": "Toronto Postal Plant (Gateway)", "province": "ON", "city": "Mississauga", "type": "Postal", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0720", "name": "Toronto Courier Facility (Mississauga)", "province": "ON", "city": "Mississauga", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0724", "name": "Brampton Courier Hub", "province": "ON", "city": "Brampton", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0740", "name": "Hamilton (John C. Munro Airport)", "province": "ON", "city": "Hamilton", "type": "Airport/Cargo", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0744", "name": "Hamilton Seaport", "province": "ON", "city": "Hamilton", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0748", "name": "Oshawa", "province": "ON", "city": "Oshawa", "type": "Inland", "clvs_release": True, "sufferance_warehouse": True},
        ]
    },

    # =========================================================================
    # SOUTHERN ONTARIO REGION (Niagara / Windsor)
    # =========================================================================
    "southern_ontario": {
        "region_name": "Southern Ontario Region",
        "regional_hq": "Windsor, ON",
        "offices": [
            # Niagara
            {"office_code": "0800", "name": "Niagara Falls (Rainbow Bridge)", "province": "ON", "city": "Niagara Falls", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0804", "name": "Queenston-Lewiston Bridge", "province": "ON", "city": "Queenston", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0808", "name": "Peace Bridge (Fort Erie)", "province": "ON", "city": "Fort Erie", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0812", "name": "Whirlpool Bridge (NEXUS)", "province": "ON", "city": "Niagara Falls", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},

            # Windsor / Detroit Corridor
            {"office_code": "0830", "name": "Ambassador Bridge", "province": "ON", "city": "Windsor", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0834", "name": "Windsor-Detroit Tunnel", "province": "ON", "city": "Windsor", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0836", "name": "Gordie Howe International Bridge", "province": "ON", "city": "Windsor", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0840", "name": "Windsor Airport", "province": "ON", "city": "Windsor", "type": "Airport", "clvs_release": True, "sufferance_warehouse": False},

            # Sarnia
            {"office_code": "0850", "name": "Blue Water Bridge (Point Edward)", "province": "ON", "city": "Point Edward", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0854", "name": "Sarnia Seaport", "province": "ON", "city": "Sarnia", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
        ]
    },

    # =========================================================================
    # PRAIRIE REGION (Manitoba / Saskatchewan)
    # =========================================================================
    "prairie": {
        "region_name": "Prairie Region",
        "regional_hq": "Winnipeg, MB",
        "offices": [
            # Manitoba
            {"office_code": "0900", "name": "Winnipeg James Armstrong Richardson Airport", "province": "MB", "city": "Winnipeg", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0904", "name": "Winnipeg Inland (Cargo/Courier)", "province": "MB", "city": "Winnipeg", "type": "Inland/Courier", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0908", "name": "Emerson (Hwy 75 / I-29)", "province": "MB", "city": "Emerson", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0912", "name": "Sprague", "province": "MB", "city": "Sprague", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "0920", "name": "Boissevain", "province": "MB", "city": "Boissevain", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "0930", "name": "Churchill (Port/Rail)", "province": "MB", "city": "Churchill", "type": "Marine/Rail", "clvs_release": False, "sufferance_warehouse": False},

            # Saskatchewan
            {"office_code": "0950", "name": "Regina International Airport", "province": "SK", "city": "Regina", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0954", "name": "Saskatoon John G. Diefenbaker Airport", "province": "SK", "city": "Saskatoon", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "0960", "name": "North Portal (Hwy 39)", "province": "SK", "city": "North Portal", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "0964", "name": "Regway", "province": "SK", "city": "Regway", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # ALBERTA REGION
    # =========================================================================
    "alberta": {
        "region_name": "Alberta Region",
        "regional_hq": "Calgary, AB",
        "offices": [
            {"office_code": "1000", "name": "Calgary International Airport", "province": "AB", "city": "Calgary", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1004", "name": "Calgary Courier Facility", "province": "AB", "city": "Calgary", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1010", "name": "Edmonton International Airport", "province": "AB", "city": "Edmonton", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1014", "name": "Edmonton Inland (Nisku)", "province": "AB", "city": "Nisku", "type": "Inland/Cargo", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1030", "name": "Coutts (Hwy 4 / I-15)", "province": "AB", "city": "Coutts", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1034", "name": "Del Bonita", "province": "AB", "city": "Del Bonita", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "1038", "name": "Carway", "province": "AB", "city": "Carway", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "1040", "name": "Chief Mountain (seasonal)", "province": "AB", "city": "Chief Mountain", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # PACIFIC REGION (British Columbia)
    # =========================================================================
    "pacific": {
        "region_name": "Pacific Region",
        "regional_hq": "Vancouver, BC",
        "offices": [
            # Vancouver Area
            {"office_code": "1100", "name": "Vancouver International Airport (YVR)", "province": "BC", "city": "Richmond", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1104", "name": "Vancouver International Mail Centre", "province": "BC", "city": "Richmond", "type": "Postal", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1108", "name": "Port of Vancouver - Vanterm", "province": "BC", "city": "Vancouver", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1110", "name": "Port of Vancouver - Centerm", "province": "BC", "city": "Vancouver", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1112", "name": "Port of Vancouver - Deltaport", "province": "BC", "city": "Delta", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1116", "name": "Port of Vancouver - Fraser Surrey Docks", "province": "BC", "city": "Surrey", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1120", "name": "Vancouver Courier Facility (Richmond)", "province": "BC", "city": "Richmond", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1124", "name": "Burnaby Courier/Cargo Hub", "province": "BC", "city": "Burnaby", "type": "Courier/CLVS", "clvs_release": True, "sufferance_warehouse": True},

            # Land Borders
            {"office_code": "1140", "name": "Pacific Highway (Surrey / Blaine)", "province": "BC", "city": "Surrey", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1144", "name": "Douglas (Peace Arch)", "province": "BC", "city": "Surrey", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1148", "name": "Huntingdon / Sumas", "province": "BC", "city": "Abbotsford", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1152", "name": "Aldergrove", "province": "BC", "city": "Aldergrove", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1160", "name": "Osoyoos", "province": "BC", "city": "Osoyoos", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1164", "name": "Kingsgate", "province": "BC", "city": "Kingsgate", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1170", "name": "Roosville", "province": "BC", "city": "Roosville", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},

            # Vancouver Island
            {"office_code": "1180", "name": "Victoria International Airport", "province": "BC", "city": "Sidney", "type": "Airport", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1184", "name": "Victoria (Sidney) Ferry", "province": "BC", "city": "Sidney", "type": "Marine/Ferry", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1188", "name": "Nanaimo Harbour", "province": "BC", "city": "Nanaimo", "type": "Marine", "clvs_release": True, "sufferance_warehouse": False},

            # Interior / Northern BC
            {"office_code": "1190", "name": "Prince Rupert (Fairview Terminal)", "province": "BC", "city": "Prince Rupert", "type": "Marine", "clvs_release": True, "sufferance_warehouse": True},
            {"office_code": "1194", "name": "Kelowna Airport", "province": "BC", "city": "Kelowna", "type": "Airport", "clvs_release": True, "sufferance_warehouse": False},
        ]
    },

    # =========================================================================
    # NORTHERN REGION (Yukon / NWT / Nunavut)
    # =========================================================================
    "northern": {
        "region_name": "Northern Region",
        "regional_hq": "Whitehorse, YT",
        "offices": [
            # Yukon
            {"office_code": "1200", "name": "Whitehorse Airport", "province": "YT", "city": "Whitehorse", "type": "Airport", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1204", "name": "Fraser (Top of the Chilkoot)", "province": "YT", "city": "Fraser", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "1208", "name": "Beaver Creek (Alaska Hwy)", "province": "YT", "city": "Beaver Creek", "type": "Land Border", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1212", "name": "Little Gold Creek", "province": "YT", "city": "Little Gold Creek", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},
            {"office_code": "1216", "name": "Pleasant Camp", "province": "YT", "city": "Pleasant Camp", "type": "Land Border", "clvs_release": False, "sufferance_warehouse": False},

            # Northwest Territories
            {"office_code": "1230", "name": "Yellowknife Airport", "province": "NT", "city": "Yellowknife", "type": "Airport", "clvs_release": True, "sufferance_warehouse": False},
            {"office_code": "1234", "name": "Inuvik Airport", "province": "NT", "city": "Inuvik", "type": "Airport", "clvs_release": False, "sufferance_warehouse": False},

            # Nunavut
            {"office_code": "1240", "name": "Iqaluit Airport", "province": "NU", "city": "Iqaluit", "type": "Airport", "clvs_release": True, "sufferance_warehouse": False},
        ]
    },
}


# =============================================================================
# Lookup Functions
# =============================================================================

def get_all_offices():
    """Return flat list of all CBSA customs offices"""
    offices = []
    for region_key, region in CBSA_CUSTOMS_OFFICES.items():
        for office in region["offices"]:
            offices.append({
                **office,
                "region": region["region_name"],
                "regional_hq": region["regional_hq"],
            })
    return offices


def get_clvs_release_offices():
    """Return offices that support CLVS release processing"""
    return [o for o in get_all_offices() if o["clvs_release"]]


def get_offices_by_province(province_code: str):
    """Return all customs offices in a given province"""
    return [o for o in get_all_offices()
            if o["province"] == province_code.upper()]


def get_offices_by_type(office_type: str):
    """Return offices matching a type (Airport, Marine, Land Border, Courier/CLVS, etc.)"""
    return [o for o in get_all_offices()
            if office_type.lower() in o["type"].lower()]


def get_office_by_code(office_code: str) -> dict | None:
    """Look up a single office by its 4-digit CBSA code"""
    for office in get_all_offices():
        if office["office_code"] == office_code:
            return office
    return None


def get_courier_hubs():
    """Return offices specifically designated as Courier/CLVS hubs"""
    return [o for o in get_all_offices()
            if "Courier" in o["type"] or "CLVS" in o["type"]]


def get_region_summary():
    """Return summary count by region"""
    summary = {}
    for region_key, region in CBSA_CUSTOMS_OFFICES.items():
        total = len(region["offices"])
        clvs = sum(1 for o in region["offices"] if o["clvs_release"])
        summary[region["region_name"]] = {
            "total_offices": total,
            "clvs_enabled": clvs,
            "regional_hq": region["regional_hq"],
        }
    return summary


if __name__ == "__main__":
    all_offices = get_all_offices()
    clvs_offices = get_clvs_release_offices()
    courier_hubs = get_courier_hubs()

    print("CBSA Designated Customs Offices Summary")
    print("=" * 60)

    for region_name, info in get_region_summary().items():
        print(f"\n  {region_name:<30} {info['total_offices']:>3} offices  "
              f"({info['clvs_enabled']} CLVS)  HQ: {info['regional_hq']}")

    print(f"\n{'Total offices:':<33} {len(all_offices)}")
    print(f"{'CLVS release enabled:':<33} {len(clvs_offices)}")
    print(f"{'Dedicated courier/CLVS hubs:':<33} {len(courier_hubs)}")

    print("\n--- Courier/CLVS Hubs ---")
    for hub in courier_hubs:
        print(f"  {hub['office_code']}  {hub['name']:<45} {hub['province']}")
