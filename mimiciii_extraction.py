import psycopg2
import pandas as pd


def extract_data(query, con):
    return pd.read_sql_query(query, con)

def clean_data(df):
    df = df.drop_duplicates()
    df = df.fillna(method='ffill')
    return df

def process_demographics(df):
    """Process demographic data, e.g., calculate age at admission."""
    df['admittime'] = pd.to_datetime(df['admittime'])
    df['dob'] = pd.to_datetime(df['dob'])
    df['age'] = (df['admittime'] - df['dob']).dt.days / 365.25
    return df

def main():
    sqluser = 'postgres'
    dbname = 'mimic'
    schema_name = 'mimiciii'

    con = psycopg2.connect(dbname=dbname, user=sqluser)

    # Set the schema for subsequent queries
    query_schema = 'set search_path to ' + schema_name + ';'
    cur = con.cursor()
    cur.execute(query_schema)
    con.commit()
    demographics_query = """
    SELECT p.subject_id, p.gender, p.dob,
           a.hadm_id, a.admittime, a.dischtime, a.deathtime, a.admission_type,
           i.icustay_id, i.intime, i.outtime, i.los
    FROM patients p
    JOIN admissions a
      ON p.subject_id = a.subject_id
    JOIN icustays i
      ON a.subject_id = i.subject_id
     AND a.hadm_id = i.hadm_id;
    """
    demographics = extract_data(demographics_query, con)
    demographics = clean_data(demographics)
    demographics = process_demographics(demographics)

    lab_query = """
    SELECT subject_id, hadm_id, itemid, valuenum, charttime
    FROM labevents
    WHERE valuenum IS NOT NULL;
    """
    labs = extract_data(lab_query, con)
    labs = clean_data(labs)
    labs['charttime'] = pd.to_datetime(labs['charttime'])

    history_query = """
    SELECT subject_id, hadm_id, icd9_code
    FROM diagnoses_icd;
    """
    history = extract_data(history_query, con)
    history = clean_data(history)

    merged_data = pd.merge(demographics, labs, on=['subject_id', 'hadm_id'], how='left')

    merged_data.to_csv('processed_patient_lab_data.csv', index=False)
    history.to_csv('processed_medical_history.csv', index=False)

    con.close()

if __name__ == '__main__':
    main()