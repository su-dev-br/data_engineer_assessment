CREATE TABLE IF NOT EXISTS home_db.HOA (
    HOA VARCHAR(255),
    HOA_Flag VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS home_db.Leads (
    Reviewed_Status VARCHAR(255),
    Most_Recent_Status VARCHAR(255),
    Source VARCHAR(255),
    Occupancy VARCHAR(255),
    Net_Yield DECIMAL(10,2),
    IRR DECIMAL(10,2),
    Selling_Reason VARCHAR(255),
    Seller_Retained_Broker VARCHAR(255),
    Final_Reviewer VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS home_db.property (
    Property_Title VARCHAR(255),
    Address VARCHAR(255),
    Market VARCHAR(255),
    Flood VARCHAR(255),
    Street_Address VARCHAR(255),
    City VARCHAR(255),
    State VARCHAR(255),
    Zip VARCHAR(20),
    Property_Type VARCHAR(255),
    Highway VARCHAR(255),
    Train VARCHAR(255),
    Tax_Rate DECIMAL(10,4),
    SQFT_Basement INT,
    HTW VARCHAR(255),
    Pool VARCHAR(255),
    Commercial VARCHAR(255),
    Water VARCHAR(255),
    Sewage VARCHAR(255),
    Year_Built INT,
    SQFT_MU INT,
    SQFT_Total INT,
    Parking VARCHAR(255),
    Bed INT,
    Bath DECIMAL(3,1),
    BasementYesNo VARCHAR(10),
    Layout VARCHAR(255),
    Rent_Restricted VARCHAR(255),
    Neighborhood_Rating VARCHAR(255),
    Latitude DECIMAL(10,7),
    Longitude DECIMAL(10,7),
    Subdivision VARCHAR(255),
    School_Average DECIMAL(3,2)
);

CREATE TABLE IF NOT EXISTS home_db.Rehab (
    Underwriting_Rehab VARCHAR(255),
    Rehab_Calculation VARCHAR(255),
    Paint VARCHAR(255),
    Flooring_Flag VARCHAR(255),
    Foundation_Flag VARCHAR(255),
    Roof_Flag VARCHAR(255),
    HVAC_Flag VARCHAR(255),
    Kitchen_Flag VARCHAR(255),
    Bathroom_Flag VARCHAR(255),
    Appliances_Flag VARCHAR(255),
    Windows_Flag VARCHAR(255),
    Landscaping_Flag VARCHAR(255),
    Trashout_Flag VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS home_db.Taxes (
    Taxes DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS home_db.Valuation (
    Previous_Rent DECIMAL(10,2),
    List_Price DECIMAL(12,2),
    Zestimate DECIMAL(12,2),
    ARV DECIMAL(12,2),
    Expected_Rent DECIMAL(10,2),
    Rent_Zestimate DECIMAL(10,2),
    Low_FMR DECIMAL(10,2),
    High_FMR DECIMAL(10,2),
    Redfin_Value DECIMAL(12,2)
);