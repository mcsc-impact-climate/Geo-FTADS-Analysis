from pathlib import Path
import os
import geopandas as gpd


def get_top_dir():
    """
    Gets the path to the top level of the git repo (one level up from the source directory)

    Parameters
    ----------
    None

    Returns
    -------
    top_dir (string): Path to the top level of the git repo

    NOTE: None
    """
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    top_dir = os.path.dirname(source_dir)
    return top_dir


def mergeShapefile(data_df, shapefile_path, on):
    """
    Merges the input shapefile with the data in data_df

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the data to be merged with the shapefile

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    """
    shapefile = gpd.read_file(shapefile_path)

    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on=on, how="left")

    return merged_dataframe


def saveShapefile(file, name):
    """
    Saves a pandas dataframe as a shapefile

    Parameters
    ----------
    file (pd.DataFrame): Dataframe to be saved as a shapefile

    name (string): Filename to the shapefile save to (must end in .shp)

    Returns
    -------
    None
    """
    # Make sure the filename ends in .shp
    if not name.endswith(".shp"):
        print(
            "ERROR: Filename for shapefile must end in '.shp'. File will not be saved."
        )
        exit()
    # Make sure the full directory path to save to exists, otherwise create it
    dir = os.path.dirname(name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    file.to_file(name)


def state_names_to_abbr(df, state_header):
    us_state_abbreviations = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "District of Columbia": "DC",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
    }

    # Replace state names with abbreviations using the dictionary
    df[state_header] = df[state_header].map(us_state_abbreviations)

    return df
