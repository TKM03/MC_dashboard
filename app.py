
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
import time
import numpy as np
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

# --- Scraping Functions ---
def wait_for_element(driver, locator):
    """Wait for an element to be clickable with a 5-second timeout."""
    return WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))

def select_date_month_day(driver, date_str, date_input_id):
    """Select a date using month-day format with reduced wait times."""
    try:
        date_to_select = datetime.strptime(date_str, '%Y-%m-%d')
        date_input = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, date_input_id)))
        date_input.click()
        month_select = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-datepicker-month')))
        month_option = month_select.find_element(By.XPATH, f"//option[@value='{date_to_select.month - 1}']")
        month_option.click()
        day = date_to_select.day
        day_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//td[@data-handler='selectDay']/a[text()='{day}']")))
        day_element.click()
        time.sleep(2)
    except Exception as e:
        print(f"Error in select_date_month_day: {str(e)}")
        raise

def select_date(driver, date_str, date_input_id):
    """Select a date using year-month-day format with reduced wait times."""
    try:
        date_to_select = datetime.strptime(date_str, '%Y-%m-%d')
        date_input = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, date_input_id)))
        date_input.click()
        time.sleep(1)
        month_select = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-datepicker-month')))
        month_option = month_select.find_element(By.XPATH, f"//option[@value='{date_to_select.month - 1}']")
        time.sleep(1)
        month_option.click()
        year_select = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-datepicker-year')))
        year_option = year_select.find_element(By.XPATH, f"//option[@value='{date_to_select.year}']")
        year_option.click()
        day = date_to_select.day
        day_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//td[@data-handler='selectDay']/a[text()='{day}']")))
        day_element.click()
        time.sleep(2)
    except Exception as e:
        print(f"Error in select_date: {str(e)}")
        raise

def extract_grid_data_clm_summary(driver):
    """Extract data from the claim summary grid with reduced delays."""
    data = []
    try:
        total_pages_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "sp_1_pjqgridClmSummbyProv")))
        total_pages = int(total_pages_element.text.strip())
    except:
        return data
    for current_page in range(1, total_pages + 1):
        time.sleep(2)  # Reduced from 3s
        driver.execute_script("window.scrollTo(0, 0);")
        grid = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "jqgridClmSummbyProv")))
        rows = WebDriverWait(grid, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.jqgrow")))
        for row in rows:
            try:
                provider_name = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridClmSummbyProv_STR_ProvName']").text
                visits = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridClmSummbyProv_STR_NoOfVisit']").text
                claim = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridClmSummbyProv_STR_ClmAmt']").text
                total_mc = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridClmSummbyProv_STR_TotalMC']").text if \
                           row.find_elements(By.CSS_SELECTOR, "td[aria-describedby='jqgridClmSummbyProv_STR_TotalMC']") else '0'
                data.append({'Provider Name': provider_name, 'No of Visits': visits, 'Total Claim': claim, 'Total MC (Days)': total_mc})
            except Exception as e:
                print(f"Error extracting row: {e}")
                continue
        if current_page < total_pages:
            try:
                next_button_div = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn.btn-sm.btn-default span.fa.fa-forward")))
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button_div)
                next_button_div.click()
                WebDriverWait(driver, 5).until(EC.staleness_of(rows[0]))  # Reduced timeout
            except:
                break
    return data

def extract_grid_data_patient_analysis(driver):
    """Extract data from the patient analysis grid with reduced delays."""
    all_data = []
    while True:
        driver.execute_script("window.scrollTo(0, 0);")
        grid = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "jqgridCorpMcAnalysis")))
        rows = grid.find_elements(By.CSS_SELECTOR, "tr.jqgrow")
        for row in rows:
            try:
                employee_name = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_MEM_NAME']").text
                employee_no = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_MEM_EMPID']").text
                division = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_MEM_EMPDIVISION']").text
                total_visit = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_totalVisit']").text
                total_mc = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_totalMC']").text
                total_claim_own = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_totalClaim_Own']").text
                total_claim_dep = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgridCorpMcAnalysis_totalClaim_Dep']").text
                all_data.append({
                    'Employee Name': employee_name, 'Employee No': employee_no, 'Division/Department': division,
                    'Total Visit': total_visit, 'Total MC (Days)': total_mc, 'Total Claim (Own)': total_claim_own,
                    'Total Claim (Dep)': total_claim_dep
                })
            except:
                continue
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn.btn-sm.btn-default span.fa.fa-forward")))
            parent_div = next_button.find_element(By.XPATH, "./parent::div")
            if "disabled" in parent_div.get_attribute("class"):
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", parent_div)
            parent_div.click()
            WebDriverWait(driver, 5).until(EC.staleness_of(rows[0]))  # Reduced timeout
        except:
            break
    return all_data

def extract_grid_data_mc(driver):
    """Extract data from the MC grid with reduced delays."""
    data = []
    try:
        total_pages_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "sp_1_jqgrid")))
        total_pages = int(total_pages_element.text.strip())
    except:
        total_pages = 1
    for current_page in range(1, total_pages + 1):
        time.sleep(2)  # Reduced from 3s
        driver.execute_script("window.scrollTo(0, 0);")
        grid = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "jqgrid")))
        rows = WebDriverWait(grid, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.jqgrow")))
        for row in rows:
            try:
                provider_name = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgrid_STR_ProvName']").text.strip()
                total_mc_given = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgrid_STR_MC_Given_Count']").text.strip()
                total_visits = row.find_element(By.CSS_SELECTOR, "td[aria-describedby='jqgrid_STR_VISITCount']").text.strip()
                data.append({'Provider': provider_name, 'Total MC Given': total_mc_given, 'No. of Visit': total_visits})
            except:
                continue
        if current_page < total_pages:
            try:
                next_button_div = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn.btn-sm.btn-default span.fa.fa-forward")))
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button_div)
                next_button_div.click()
                WebDriverWait(driver, 5).until(EC.staleness_of(rows[0]))  # Reduced timeout
            except:
                break
    return data

def scrape_data(url, user_id, password):
    """Scrape data from the website using Firefox WebDriver in headless mode."""
    firefox_options = FirefoxOptions()
    firefox_options.add_argument('--headless')  # Run Firefox in headless mode
    firefox_options.add_argument('--no-sandbox')  # Disable sandbox for better compatibility in cloud environments
    firefox_options.add_argument('--disable-gpu')  # Disable GPU to prevent issues in headless mode

    # Use GeckoDriverManager without specifying driver_version, letting it auto-select
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),  # Auto-select the latest compatible version
        options=firefox_options
    )
    
    start_year = 2024
    current_date = datetime.now().strftime('%Y-%m-%d')
    patient_data_by_year = {}
    claim_data_by_year = {}
    mc_data_by_year = {}
    try:
        print("Starting scrape...")
        driver.get(url)
        image = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//img[@src='/ClaimEXMVR/Servlet_LoadImage?SFC=loadImage&imageName=icorporate.png']")))
        image.click()
        user_id_field = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "txtloginid")))
        user_id_field.send_keys(user_id)
        password_field = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "inputpss")))
        password_field.send_keys(password)
        sign_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")))
        sign_button.click()
        continue_button = wait_for_element(driver, (By.XPATH, "//button[text()='Continue']"))
        continue_button.click()

        # Only scrape 2024 for testing (remove 2025 to speed up)
        year = 2024
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        # Patient analysis for 2024
        print("Navigating to patient analysis...")
        productivity_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Productivity Reports']]")))
        productivity_link.click()
        patient_analysis_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#/Patient_Analysis_Report'][span[text()=' Patient Analysis Report ']]")))
        patient_analysis_link.click()
        select_date(driver, start_date, "txtStartDate")
        select_date(driver, end_date, "txtEndDate")
        search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnSearch")))
        search_button.click()
        time.sleep(2)
        dropdown = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.ui-pg-selbox")))
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        select = Select(dropdown)
        select.select_by_value("10")  # Reduced page size for speed
        time.sleep(2)
        print("Extracting patient data...")
        patient_data = extract_grid_data_patient_analysis(driver)
        patient_df = pd.DataFrame(patient_data)
        numeric_cols_patient = ['Total Visit', 'Total MC (Days)', 'Total Claim (Own)', 'Total Claim (Dep)']
        for col in numeric_cols_patient:
            patient_df[col] = pd.to_numeric(patient_df[col], errors='coerce')
        patient_df['Total Claim (Combined)'] = patient_df['Total Claim (Own)'] + patient_df['Total Claim (Dep)']
        patient_data_by_year[year] = patient_df

        # MC data for 2024 (optional, remove or limit for testing)
        print("Navigating to MC by Provider...")
        productivity_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Productivity Reports']]")))
        productivity_link.click()
        mc_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#/MC_HealthCare_By_Provider'][span[text()=' MC by Provider ']]")))
        mc_link.click()
        time.sleep(1)
        select_date(driver, start_date, "txtStartDate")
        select_date(driver, end_date, "txtEndDate")
        search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnSearch")))
        search_button.click()
        time.sleep(2)
        dropdown = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.ui-pg-selbox")))
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        select = Select(dropdown)
        select.select_by_value("10")  # Reduced page size
        time.sleep(2)
        print("Extracting MC data...")
        mc_data = extract_grid_data_mc(driver)
        mc_df = pd.DataFrame(mc_data)
        numeric_cols_mc = ['Total MC Given', 'No. of Visit']
        for col in numeric_cols_mc:
            mc_df[col] = pd.to_numeric(mc_df[col], errors='coerce')
        mc_df['% MC Given'] = (mc_df['Total MC Given'] / mc_df['No. of Visit']) * 100
        mc_data_by_year[year] = mc_df

        # Claim summary for 2024 (optional, limit for testing)
        print("Navigating to claim summary...")
        reg_claims_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(text(), 'Registration') and contains(text(), 'Claims')]]")))
        reg_claims_link.click()
        providers_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#/Claim_Summary_by_Provider_Analysis'][span[text()=' Claim Summary by Providers ']]")))
        providers_link.click()
        time.sleep(2)
        select_date_month_day(driver, start_date, "txtFromDate")
        select_date_month_day(driver, "2024-12-31", "txtToDate")  # Limit to 2024
        search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnSearch")))
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(2)
        dropdown = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.ui-pg-selbox")))
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        select = Select(dropdown)
        select.select_by_value("10")  # Reduced page size
        time.sleep(2)
        print("Extracting claim data...")
        claim_data_2024 = extract_grid_data_clm_summary(driver)
        claim_df_2024 = pd.DataFrame(claim_data_2024)
        numeric_cols_claim = ['No of Visits', 'Total Claim', 'Total MC (Days)']
        for col in numeric_cols_claim:
            claim_df_2024[col] = pd.to_numeric(claim_df_2024[col], errors='coerce')
        claim_df_2024['Avg Claim per Visit'] = claim_df_2024['Total Claim'] / claim_df_2024['No of Visits']
        claim_data_by_year[2024] = claim_df_2024

        print("Scraping complete!")
        return patient_data_by_year, claim_data_by_year, mc_data_by_year, "Data scraped successfully!"
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None, None, f"Error: {str(e)}"
    finally:
        driver.quit()

# --- Plotting Functions ---
def generate_dashboard_charts(patient_data_by_year, claim_data_by_year, mc_data_by_year, year):
    if not patient_data_by_year or not claim_data_by_year or not mc_data_by_year:
        return None, None
    
    year_int = int(year)
    patient_df = patient_data_by_year.get(year_int, pd.DataFrame())
    claim_df = claim_data_by_year.get(year_int, pd.DataFrame())
    mc_df = mc_data_by_year.get(year_int, pd.DataFrame())
    
    if patient_df.empty or claim_df.empty or mc_df.empty:
        return None, None
    
    sns.set(style="whitegrid", palette="deep")
    provider_charts = []
    employee_charts = []

    # --- Provider Dashboard Charts ---
    # 1. Total Visits by Providers
    fig, ax = plt.subplots(figsize=(10, 6))
    top_prov_visits = mc_df.sort_values('No. of Visit', ascending=False).head(10)
    sns.barplot(data=top_prov_visits, x='No. of Visit', y='Provider', hue='Provider', palette='Blues_d', legend=False)
    plt.title(f'Top 10 Providers by Total Visits ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total Visits', fontsize=12)
    plt.ylabel('Provider', fontsize=12)
    for i, v in enumerate(top_prov_visits['No. of Visit']):
        plt.text(v + 1, i, f'{int(v)}', va='center', fontsize=10)
    plt.tight_layout()
    provider_charts.append(fig)

    # 2. Total MC by Providers
    fig, ax = plt.subplots(figsize=(10, 6))
    top_prov_mc = mc_df.sort_values('Total MC Given', ascending=False).head(10)
    sns.barplot(data=top_prov_mc, x='Total MC Given', y='Provider', hue='Provider', palette='Greens_d', legend=False)
    plt.title(f'Top 10 Providers by Total MC Given ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total MC (Days)', fontsize=12)
    plt.ylabel('Provider', fontsize=12)
    for i, v in enumerate(top_prov_mc['Total MC Given']):
        plt.text(v + 1, i, f'{int(v)}', va='center', fontsize=10)
    plt.tight_layout()
    provider_charts.append(fig)

    # 3. % MC Given by Providers
    fig, ax = plt.subplots(figsize=(10, 6))
    top_prov_mc_pct = mc_df.sort_values('% MC Given', ascending=False).head(10)
    sns.barplot(data=top_prov_mc_pct, x='Provider', y='% MC Given', hue='Provider', palette='Purples_d', legend=False)
    plt.title(f'Top 10 Providers by % MC Given ({year})', fontsize=14, weight='bold')
    plt.ylabel('% MC Given', fontsize=12)
    plt.xlabel('Provider', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_prov_mc_pct['% MC Given']):
        plt.text(i, v + 1, f'{v:.1f}%', ha='center', fontsize=10)
    plt.tight_layout()
    provider_charts.append(fig)

    # 4. Total Claim by Providers
    fig, ax = plt.subplots(figsize=(10, 6))
    top_prov_claim = claim_df.sort_values('Total Claim', ascending=False).head(10)
    sns.barplot(data=top_prov_claim, x='Total Claim', y='Provider Name', hue='Provider Name', palette='Oranges_d', legend=False)
    plt.title(f'Top 10 Providers by Total Claim ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total Claim ($)', fontsize=12)
    plt.ylabel('Provider', fontsize=12)
    for i, v in enumerate(top_prov_claim['Total Claim']):
        plt.text(v + 1, i, f'{v:.2f}', va='center', fontsize=10)
    plt.tight_layout()
    provider_charts.append(fig)

    # 5. Average Claim per Visit by Providers
    fig, ax = plt.subplots(figsize=(10, 6))
    top_prov_avg_claim = claim_df.sort_values('Avg Claim per Visit', ascending=False).head(10)
    sns.barplot(data=top_prov_avg_claim, x='Provider Name', y='Avg Claim per Visit', hue='Provider Name', palette='Reds_d', legend=False)
    plt.title(f'Top 10 Providers by Avg Claim per Visit ({year})', fontsize=14, weight='bold')
    plt.ylabel('Avg Claim per Visit ($)', fontsize=12)
    plt.xlabel('Provider', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_prov_avg_claim['Avg Claim per Visit']):
        plt.text(i, v + 0.5, f'{v:.2f}', ha='center', fontsize=10)
    plt.tight_layout()
    provider_charts.append(fig)

    # 6. MC vs Claim Correlation
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=claim_df, x='Total MC (Days)', y='Total Claim', size='No of Visits', hue='Provider Name', palette='viridis', legend=False)
    plt.title(f'MC vs Claim by Provider ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total MC (Days)', fontsize=12)
    plt.ylabel('Total Claim ($)', fontsize=12)
    plt.tight_layout()
    provider_charts.append(fig)

    # --- Employee Dashboard Charts ---
    # 1. Total Visits by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_visits = patient_df.sort_values('Total Visit', ascending=False).head(10)
    sns.barplot(data=top_emp_visits, x='Total Visit', y='Employee Name', hue='Employee Name', palette='Blues_d', legend=False)
    plt.title(f'Top 10 Employees by Total Visits ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total Visits', fontsize=12)
    plt.ylabel('Employee', fontsize=12)
    for i, v in enumerate(top_emp_visits['Total Visit']):
        plt.text(v + 0.2, i, f'{int(v)}', va='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 2. Total Claim by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_claim = patient_df.sort_values('Total Claim (Combined)', ascending=False).head(10)
    sns.barplot(data=top_emp_claim, x='Total Claim (Combined)', y='Employee Name', hue='Employee Name', palette='Oranges_d', legend=False)
    plt.title(f'Top 10 Employees by Total Claim ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total Claim ($)', fontsize=12)
    plt.ylabel('Employee', fontsize=12)
    for i, v in enumerate(top_emp_claim['Total Claim (Combined)']):
        plt.text(v + 1, i, f'{v:.2f}', va='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 3. Average Claim per Visit by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_avg_claim = patient_df.sort_values('Avg Claim per Visit', ascending=False).head(10)
    sns.barplot(data=top_emp_avg_claim, x='Employee Name', y='Avg Claim per Visit', hue='Employee Name', palette='Reds_d', legend=False)
    plt.title(f'Top 10 Employees by Avg Claim per Visit ({year})', fontsize=14, weight='bold')
    plt.ylabel('Avg Claim per Visit ($)', fontsize=12)
    plt.xlabel('Employee', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_emp_avg_claim['Avg Claim per Visit']):
        plt.text(i, v + 0.5, f'{v:.2f}', ha='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 4. Total MC by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_mc = patient_df.sort_values('Total MC (Days)', ascending=False).head(10)
    sns.barplot(data=top_emp_mc, x='Total MC (Days)', y='Employee Name', hue='Employee Name', palette='Greens_d', legend=False)
    plt.title(f'Top 10 Employees by Total MC ({year})', fontsize=14, weight='bold')
    plt.xlabel('Total MC (Days)', fontsize=12)
    plt.ylabel('Employee', fontsize=12)
    for i, v in enumerate(top_emp_mc['Total MC (Days)']):
        plt.text(v + 0.2, i, f'{int(v)}', va='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 5. Average MC per Visit by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_avg_mc = patient_df.sort_values('Avg MC per Visit', ascending=False).head(10)
    sns.barplot(data=top_emp_avg_mc, x='Employee Name', y='Avg MC per Visit', hue='Employee Name', palette='Purples_d', legend=False)
    plt.title(f'Top 10 Employees by Avg MC per Visit ({year})', fontsize=14, weight='bold')
    plt.ylabel('Avg MC per Visit (Days)', fontsize=12)
    plt.xlabel('Employee', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_emp_avg_mc['Avg MC per Visit']):
        plt.text(i, v + 0.05, f'{v:.2f}', ha='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 6. Average Claim per MC by Employees
    fig, ax = plt.subplots(figsize=(10, 6))
    top_emp_avg_claim_mc = patient_df.sort_values('Avg Claim per MC', ascending=False).head(10)
    sns.barplot(data=top_emp_avg_claim_mc, x='Employee Name', y='Avg Claim per MC', hue='Employee Name', palette='YlOrBr', legend=False)
    plt.title(f'Top 10 Employees by Avg Claim per MC ({year})', fontsize=14, weight='bold')
    plt.ylabel('Avg Claim per MC ($)', fontsize=12)
    plt.xlabel('Employee', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    for i, v in enumerate(top_emp_avg_claim_mc['Avg Claim per MC']):
        plt.text(i, v + 0.5, f'{v:.2f}', ha='center', fontsize=10)
    plt.tight_layout()
    employee_charts.append(fig)

    # 7. Division-wise Claim Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    division_claims = patient_df.groupby('Division/Department')['Total Claim (Combined)'].sum()
    plt.pie(division_claims, labels=division_claims.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'), startangle=90)
    plt.title(f'Claim Distribution by Division ({year})', fontsize=14, weight='bold')
    plt.tight_layout()
    employee_charts.append(fig)

    return provider_charts, employee_charts

# --- Streamlit Interface ---
def main():
    st.set_page_config(page_title="Claims Analysis Dashboard", layout="wide")

    if 'data_loaded' not in st.session_state:
        st.session_state['data_loaded'] = False
        st.session_state['patient_data'] = {}
        st.session_state['claim_data'] = {}
        st.session_state['mc_data'] = {}
        st.session_state['selected_year'] = "2024"

    with st.sidebar:
        st.title("Claims Analysis Dashboard")
        st.subheader("Login Details")
        
        # Use Streamlit secrets for deployment, fall back to user input for local testing
        url = st.secrets.get("URL", "") if st.secrets else st.text_input("Website URL", key="url", value="http:")  # Default to your provided URL
        user_id = st.secrets.get("USER_ID", "") if st.secrets else st.text_input("User ID", key="user_id", value="")  # Default to your provided USER_ID
        password = st.secrets.get("PASSWORD", "") if st.secrets else st.text_input("Password", type="password", key="password", value="")  # Default to your provided PASSWORD
        
        if st.button("Scrape Data", key="scrape_button"):
            if not all([url, user_id, password]):
                st.error("Please fill in all login details")
            else:
                with st.spinner("Scraping data... This may take a few minutes."):
                    patient_data_by_year, claim_data_by_year, mc_data_by_year, status = scrape_data(url, user_id, password)
                    if patient_data_by_year and claim_data_by_year and mc_data_by_year:
                        st.session_state['patient_data'] = patient_data_by_year
                        st.session_state['claim_data'] = claim_data_by_year
                        st.session_state['mc_data'] = mc_data_by_year
                        st.session_state['data_loaded'] = True
                        st.success(status)
                    else:
                        st.error(status)
                        st.session_state['data_loaded'] = False
        
        if st.session_state['data_loaded']:
            year = st.selectbox("Select Year", options=["2024", "2025"], index=0, key="year_select")
            st.session_state['selected_year'] = year

    st.title("Healthcare Claims Analysis Dashboard")
    
    if not st.session_state['data_loaded']:
        st.info("Please enter your credentials and click 'Scrape Data' to begin.")
        return

    tab1, tab2 = st.tabs(["Provider Insights", "Employee Insights"])
    year = st.session_state['selected_year']
    provider_charts, employee_charts = generate_dashboard_charts(
        st.session_state['patient_data'], st.session_state['claim_data'], st.session_state['mc_data'], year
    )

    if not provider_charts or not employee_charts:
        st.error("Failed to generate charts. Please check the scraped data.")
        return

    with tab1:
        st.header(f"Provider Insights Dashboard ({year})")
        col1, col2 = st.columns(2)
        for i in range(0, len(provider_charts), 2):
            with col1:
                st.pyplot(provider_charts[i])
            if i + 1 < len(provider_charts):
                with col2:
                    st.pyplot(provider_charts[i + 1])

    with tab2:
        st.header(f"Employee Insights Dashboard ({year})")
        col1, col2 = st.columns(2)
        for i in range(0, len(employee_charts), 2):
            with col1:
                st.pyplot(employee_charts[i])
            if i + 1 < len(employee_charts):
                with col2:
                    st.pyplot(employee_charts[i + 1])

if __name__ == "__main__":
    main()
