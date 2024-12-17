import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

# Sidebar for student info
def sidebar_navigation():
    st.sidebar.title("Supply Chain Simulation")
    student_name = st.sidebar.text_input("Student Name", value="")
    student_number = st.sidebar.text_input("Student Number", value="")
    return student_name, student_number

# Initialize Streamlit session states
def initialize_session_state():
    if "final_decisions" not in st.session_state:
        st.session_state.final_decisions = []
    if "locked" not in st.session_state:
        st.session_state.locked = False
    if 'saved_simulations' not in st.session_state:
        st.session_state['saved_simulations'] = []

# Track company decisions and metrics
def track_decisions(student_name, student_number, metrics, period):
    # Append new decision with metrics for the company
    decision = {
        "Student Name": student_name,
        "Student Number": student_number,
        "Period": period,
        **metrics
    }
    st.session_state.final_decisions.append(decision)

# Calculate score based on performance metrics
def calculate_score(metrics):
    max_cost = 20000
    max_lead_time = 30

    cost_score = max(0, min(10, 10 - (metrics["Cost"] / max_cost) * 10))
    lead_time_score = max(0, min(10, 10 - (metrics["Lead Time"] / max_lead_time) * 10))

    score = (
        metrics["Responsiveness"] * 0.2 +
        max(0, metrics["Efficiency"]) * 0.2 +
        cost_score * 0.15 +
        lead_time_score * 0.15 +
        metrics["Customer Satisfaction"] * 0.2 +
        (10 - metrics["Environmental Impact"]) * 0.1
    )

    return max(0, min(100, round(score, 2)))  # Scale score to 0-100

# Function to get scenario parameters
def get_scenario_parameters(scenario):
    if scenario == "Stable Market":
        return {
            "demand_growth_rate": 0.0,
            "supply_disruption": False,
            "competitor_price_change": 0.0
        }
    elif scenario == "Increasing Demand":
        return {
            "demand_growth_rate": 0.05,  # 5% increase each period
            "supply_disruption": False,
            "competitor_price_change": 0.0
        }
    elif scenario == "Supply Disruption":
        return {
            "demand_growth_rate": 0.0,
            "supply_disruption": True,
            "disruption_period": 3,  # Disruption occurs at period 3
            "competitor_price_change": 0.0
        }
    elif scenario == "Price Competition":
        return {
            "demand_growth_rate": 0.0,
            "supply_disruption": False,
            "competitor_price_change": -0.1  # Competitor reduces price by 10%
        }
    else:
        # Default parameters
        return {
            "demand_growth_rate": 0.0,
            "supply_disruption": False,
            "competitor_price_change": 0.0
        }

# Function to check for random events
def check_for_random_events(period):
    event_occurred = False
    event_description = ""

    # 20% chance of an event occurring each period
    if random.random() < 0.2:
        event_occurred = True
        event = random.choice(["Transportation Strike", "Regulatory Change", "Technology Advancement"])
        if event == "Transportation Strike":
            event_description = "A transportation strike has occurred, increasing lead times!"
            event_effects = {"Lead Time": 5}
        elif event == "Regulatory Change":
            event_description = "New regulations have increased operational costs."
            event_effects = {"Cost": 1000}
        elif event == "Technology Advancement":
            event_description = "A new technology has improved efficiency."
            event_effects = {"Efficiency": 1}
    else:
        event_effects = {}

    return event_occurred, event_description, event_effects

# Dynamic plot for visualizing trade-offs
def show_simulation_results(metrics_df):
    # Radar chart for the last period
    latest_metrics = metrics_df.iloc[-1]

    max_cost = 20000  # Maximum cost
    max_lead_time = 30  # Maximum lead time

    categories = ['Responsiveness', 'Efficiency', 'Normalized Cost', 'Normalized Lead Time', 'Environmental Impact', 'Customer Satisfaction']
    values = [
        latest_metrics['Responsiveness'],
        latest_metrics['Efficiency'],
        max(0, min(10, 10 - (latest_metrics['Cost'] / max_cost) * 10)),  # Normalized Cost Score
        max(0, min(10, 10 - (latest_metrics['Lead Time'] / max_lead_time) * 10)),  # Normalized Lead Time Score
        latest_metrics['Environmental Impact'],
        latest_metrics['Customer Satisfaction']
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance Metrics'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Performance Metrics Radar Chart"
    )

    st.plotly_chart(fig)

    # Line charts over time
    st.markdown("### Performance Over Time")
    metrics_to_plot = ['Responsiveness', 'Efficiency', 'Environmental Impact', 'Customer Satisfaction', 'Score']
    fig2 = px.line(metrics_df, x='Period', y=metrics_to_plot, markers=True, title='Performance Metrics Over Time')
    st.plotly_chart(fig2)

    # Plot Cost and Lead Time separately
    fig3 = px.line(metrics_df, x='Period', y=['Cost', 'Lead Time'], markers=True, title='Cost and Lead Time Over Time')
    st.plotly_chart(fig3)

# Interactive simulation function
def interactive_simulation(student_name, student_number, scenario):
    st.header("Interactive Supply Chain Simulation")

    # Get scenario parameters
    scenario_params = get_scenario_parameters(scenario)

    description = f"""
        **Scenario: {scenario}**

        You are the CEO of **TechPro Electronics**, tasked with optimizing your supply chain over the next **12 months**. Under the **{scenario}** scenario, you can adjust various decision parameters each month to see how they affect your company's performance over time.

        **Instructions:**

        - Use the sliders and dropdowns to adjust your decisions for each period.
        - Click the **Run Simulation** button to process your inputs.
        - Observe how your choices impact the performance metrics and overall company performance.
        - Aim to achieve a balance between responsiveness, efficiency, cost, lead time, customer satisfaction, and environmental impact.

        **Decision Parameters:**

        1. **Production Capacity Change (%)**: Adjust the percentage increase or decrease in production capacity.
        2. **Inventory Level (%)**: Set the desired inventory level as a percentage of forecasted demand.
        3. **Transportation Mode**: Choose between Air, Sea, or a mix of both.
        4. **Number of Suppliers**: Decide how many suppliers to source from (1 to 5).
        5. **Pricing Discount (%)**: Set the percentage discount offered to customers.
    """
    st.write(description)

    # Embedded learning materials
    with st.expander("Understanding Supply Chain Trade-offs"):
        st.write("""
        In supply chain management, trade-offs often occur between different performance metrics. For example, increasing responsiveness may lead to higher costs. It's important to balance these metrics based on the company's strategic objectives.
        """)
        #st.markdown("[Learn more about supply chain trade-offs](https://example.com/supply-chain-trade-offs)")

    # Simulation over selected periods
    periods = st.slider("Select the number of periods to simulate (months):", min_value=1, max_value=12, value=6)

    # Create a form to collect inputs
    with st.form("simulation_form"):
        inputs = []
        for period in range(1, periods + 1):
            st.markdown(f"### Period {period}")

            production_capacity_change = st.slider(
                f"Production Capacity Change (%) - Period {period}",
                min_value=-20,
                max_value=50,
                value=0,
                key=f"production_capacity_{period}",
                help="Adjust the production capacity to meet changing demand. Increasing capacity may increase costs."
            )

            inventory_level = st.slider(
                f"Inventory Level (%) - Period {period}",
                min_value=50,
                max_value=150,
                value=100,
                key=f"inventory_level_{period}",
                help="Set the inventory level as a percentage of the forecasted demand."
            )

            transportation_mode = st.selectbox(
                f"Transportation Mode - Period {period}",
                options=["Air", "Sea", "Mixed"],
                key=f"transportation_mode_{period}",
                help="Choose a transportation mode. Air is faster but more expensive and less environmentally friendly."
            )

            number_of_suppliers = st.slider(
                f"Number of Suppliers - Period {period}",
                min_value=1,
                max_value=5,
                value=2,
                key=f"suppliers_{period}",
                help="Select the number of suppliers to source from. More suppliers can reduce risk but may increase complexity."
            )

            pricing_discount = st.slider(
                f"Pricing Discount (%) - Period {period}",
                min_value=0,
                max_value=30,
                value=0,
                key=f"pricing_discount_{period}",
                help="Set the discount percentage offered to customers."
            )

            inputs.append({
                'period': period,
                'production_capacity_change': production_capacity_change,
                'inventory_level': inventory_level,
                'transportation_mode': transportation_mode,
                'number_of_suppliers': number_of_suppliers,
                'pricing_discount': pricing_discount
            })

        # Submit button inside the form
        submitted = st.form_submit_button("Run Simulation")

    if submitted:
        # Store inputs in session state
        st.session_state['simulation_inputs'] = inputs

        # Initialize variables for demand and other factors
        base_demand = 1000  # Starting demand
        demand = base_demand
        metrics_list = []

        for input_data in inputs:
            period = input_data['period']

            # Adjust demand based on scenario
            demand *= (1 + scenario_params['demand_growth_rate'])

            # Base metrics
            metrics = {
                "Period": period,
                "Demand": demand,
                "Responsiveness": 5,
                "Efficiency": 5,
                "Cost": 5000,
                "Lead Time": 15,
                "Environmental Impact": 5
            }

            # Handle supply disruption
            if scenario_params.get('supply_disruption') and period == scenario_params.get('disruption_period'):
                st.warning(f"Supply disruption occurred in Period {period}!")
                # Increase lead time and cost
                metrics["Lead Time"] += 5
                metrics["Cost"] += 2000

            # Adjustments based on decisions
            # Production Capacity
            metrics["Responsiveness"] += input_data['production_capacity_change'] * 0.05
            metrics["Cost"] += abs(input_data['production_capacity_change']) * 50

            # Inventory Level
            metrics["Lead Time"] -= (input_data['inventory_level'] - 100) * 0.05
            metrics["Cost"] += (input_data['inventory_level'] - 100) * 20

            # Transportation Mode
            if input_data['transportation_mode'] == "Air":
                metrics["Lead Time"] -= 5
                metrics["Cost"] += 2000
                metrics["Environmental Impact"] += 2
                metrics["Responsiveness"] += 2
            elif input_data['transportation_mode'] == "Sea":
                metrics["Lead Time"] += 3
                metrics["Cost"] -= 500
                metrics["Environmental Impact"] -= 1
                metrics["Responsiveness"] -= 1
            else:  # Mixed
                metrics["Cost"] += 500
                metrics["Environmental Impact"] += 0.5

            # Number of Suppliers
            metrics["Efficiency"] += (3 - input_data['number_of_suppliers']) * 0.5
            metrics["Cost"] += input_data['number_of_suppliers'] * 100
            metrics["Environmental Impact"] += input_data['number_of_suppliers'] * 0.2

            # Pricing Discount
            metrics["Responsiveness"] += input_data['pricing_discount'] * 0.1
            metrics["Cost"] -= input_data['pricing_discount'] * 50

            # Apply competitor price change
            if scenario_params.get('competitor_price_change', 0.0) != 0.0:
                st.info(f"Competitor has changed their prices by {abs(scenario_params['competitor_price_change'] * 100)}%")
                metrics["Cost"] -= scenario_params['competitor_price_change'] * 1000  # Simplified effect

            # Check for random events
            event_occurred, event_description, event_effects = check_for_random_events(period)
            if event_occurred:
                st.info(f"**Period {period} Event:** {event_description}")
                # Apply event effects to metrics
                for key, value in event_effects.items():
                    metrics[key] += value

            # Ensure metrics are within realistic bounds
            metrics["Responsiveness"] = max(0, min(10, metrics["Responsiveness"]))
            metrics["Efficiency"] = max(0, min(10, metrics["Efficiency"]))
            metrics["Environmental Impact"] = max(0, min(10, metrics["Environmental Impact"]))
            metrics["Lead Time"] = max(1, metrics["Lead Time"])  # Lead Time should not be less than 1 day

            # Calculate additional metrics
            metrics["Customer Satisfaction"] = max(0, min(10, 10 - metrics["Lead Time"] * 0.5))
            metrics["Sales Revenue"] = demand * (1 - input_data['pricing_discount'] / 100) * 10  # Simplified revenue calculation
            metrics["Profit Margin"] = ((metrics["Sales Revenue"] - metrics["Cost"]) / metrics["Sales Revenue"]) * 100

            # Calculate score
            score = calculate_score(metrics)
            metrics["Score"] = score

            # Track decisions and metrics
            track_decisions(student_name, student_number, metrics, period)
            metrics_list.append(metrics)

        # Convert final decisions to DataFrame
        df_metrics = pd.DataFrame(metrics_list)
        df_metrics.sort_values(by='Period', inplace=True)

        # Store the results in session state
        st.session_state['simulation_results'] = df_metrics

        # Display the results
        st.markdown("## Simulation Results")
        st.dataframe(df_metrics[['Period', 'Demand', 'Responsiveness', 'Efficiency', 'Cost', 'Lead Time', 'Environmental Impact', 'Customer Satisfaction', 'Profit Margin', 'Score']])

        show_simulation_results(df_metrics)

        # Provide download option
        csv = df_metrics.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Simulation Results as CSV",
            data=csv,
            file_name=f'{student_name}_{student_number}_simulation_results.csv',
            mime='text/csv',
        )

        # Save simulation
        save_simulation = st.button("Save Simulation for Comparison")
        if save_simulation:
            st.session_state['saved_simulations'].append({
                'scenario': scenario,
                'metrics_df': df_metrics
            })
            st.success("Simulation saved for comparison.")

        # Lock decisions to prevent changes
        st.session_state.locked = True

    # Display saved simulations for comparison
    if st.session_state['saved_simulations']:
        st.markdown("## Saved Simulations")
        for idx, sim in enumerate(st.session_state['saved_simulations']):
            st.write(f"### Simulation {idx + 1} - Scenario: {sim['scenario']}")
            st.dataframe(sim['metrics_df'][['Period', 'Score']])

# Function to display project guidelines
def display_project_guidelines():
    st.header("Project Guidelines")

    # Use expander to organize content
    with st.expander("Evaluation Rubric"):
        st.markdown("""
        ### Evaluation Criteria (Total: 100 Points)

        **Simulation Performance (40%)**

        - **Balanced Metrics (20%)**: Did you achieve a well-balanced supply chain performance?
        - **Improvement Over Time (10%)**: Did you improve over the periods in the simulation?
        - **Adaptation to Scenarios (10%)**: Did you adapt strategies to different scenarios/events?

        **Decision-Making Process (50%)**

        - **Strategic Thinking (20%)**: How well did you explain and justify your decisions?
        - **Data Analysis (15%)**: How well did you analyze data and adjust strategies accordingly?
        - **Connection to Theory (15%)**: Did you relate your decisions to supply chain theories?

        **Reflective Report (10%)**

        - **Report Quality (10%)**: Is your report clear, organized, and insightful?
        """)

    with st.expander("Student Report Template"):
        st.markdown("""
        ### Supply Chain Simulation Report

        **Name:** [Your Name]  
        **Student Number:** [Your Student Number]

        **1. Introduction**

        - Objective of the simulation.
        - Scenario chosen.
        - Overview of your goals.

        **2. Strategy and Decision-Making**

        - Key decisions made in each period.
        - Trade-offs considered.

        **3. Analysis of Results**

        - Presentation of performance metrics.
        - Evaluation of outcomes.

        **4. Reflection on Learning**

        - Lessons learned.
        - Strengths and weaknesses.
        - Adaptation to events.

        **5. Connection to Theory**

        - Application of supply chain theories.
        - Real-world implications.

        **6. Conclusion**

        - Summary of findings.
        - Future strategies.

        **7. References**

        - Any sources used.

        *Please format your report accordingly and submit it as a PDF.*
        """)

    with st.expander("Guidelines for Submission"):
        st.markdown("""
        **Submission Requirements:**

        1. **Simulation Data**: Submit the CSV files from your simulation runs.
        2. **Reflective Report**: Submit a PDF of your reflective report.
        3. **File Naming**: 
           - CSV: `[YourName]_[StudentNumber]_simulation_results.csv`
           - Report: `[YourName]_[StudentNumber]_simulation_report.pdf`
        4. **Deadline**: All files must be submitted by [Insert Deadline Date].
        5. **Submission Method**: [Insert Submission Instructions].

        **Number of Simulations Required:**

        - At least **two simulation runs**:
          - **First Simulation**: Initial attempt.
          - **Second Simulation**: Refined strategy after analysis.

        *You are encouraged to run additional simulations to explore different strategies.*
        """)

    with st.expander("Expected Outcomes and Example Solutions"):
        st.markdown("""
        ### Stable Market Scenario

        - **Focus**: Efficiency and cost control.
        - **Optimal Strategy**:
          - Steady production capacity.
          - Sea freight for cost-effectiveness.
          - Moderate inventory levels.
          - Supplier consolidation.

        ### Increasing Demand Scenario

        - **Focus**: Scaling up production and maintaining responsiveness.
        - **Optimal Strategy**:
          - Gradual increase in production capacity and inventory.
          - Use air freight during peak periods.
          - Multi-source suppliers.

        ### Supply Disruption Scenario

        - **Focus**: Risk management and resilience.
        - **Optimal Strategy**:
          - Increase inventory levels.
          - Diversify suppliers.
          - Use air freight during disruptions.

        ### Price Competition Scenario

        - **Focus**: Adjusting pricing strategy while maintaining margins.
        - **Optimal Strategy**:
          - Strategic discounts.
          - Focus on efficiency to reduce costs.
          - Multi-source suppliers.
        """)

# Main simulation flow for individual students
def run_simulation():
    st.title("Interactive Supply Chain Simulation Project")

    # Initialize session state
    initialize_session_state()

    # Sidebar for student info
    student_name, student_number = sidebar_navigation()

    if student_name and student_number:
        st.markdown("---")

        # Scenario selection
        scenario = st.selectbox(
            "Select a Scenario",
            options=["Stable Market", "Increasing Demand", "Supply Disruption", "Price Competition"],
            help="Choose a market scenario to simulate."
        )

        # Navigation tabs
        tab1, tab2 = st.tabs(["Simulation", "Project Guidelines"])

        with tab1:
            interactive_simulation(student_name, student_number, scenario)

            # Provide feedback
            st.markdown("## Provide Your Feedback")
            feedback = st.text_area("What did you learn from this simulation? Do you have any suggestions?")
            submit_feedback = st.button("Submit Feedback")
            if submit_feedback:
                # In a real application, save feedback to a database or file
                st.success("Thank you for your feedback!")

        with tab2:
            display_project_guidelines()

    else:
        st.info("Please enter your student name and student number in the sidebar to begin.")
    st.sidebar.info("*created by* **Çiğdem Sıcakyüz**, 10/12/2024")
if __name__ == "__main__":
    run_simulation()
