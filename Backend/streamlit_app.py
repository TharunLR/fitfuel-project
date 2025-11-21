import streamlit as st
import pandas as pd

from random import uniform as rnd
from ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts
from one import recommend,output_recommended_recipes
# 🟩 Custom CSS styling for Streamlit input boxes
st.markdown("""
    <style>
        /* General input box styling (text_input, number_input) */
       div[data-baseweb="input"] > div {
    background-color: #AFEEEE;   /* Light turquoise (soft on eyes) */
    color: #002B36;              /* Dark teal text (readable) */
    border-radius: px;         /* Smooth, modern rounded corners */
    border: 4px solid black;   /* Matching turquoise border */
}
/* Number input special case – full border visible */
div[data-baseweb="input-number"] {
    border: 3px solid #00CED1;   /* Outer border (all sides visible) */
    border-radius: 12px;
    background-color: #E0FFFF;   /* Match inner background */
    padding: 20px;                /* Small padding to avoid clipping */
}

/* Inner content box styling */
div[data-baseweb="input-number"] > div {
    background-color: #E0FFFF;
    color: #000000;
    border-radius: 10px;
    border: none;                /* Remove inner partial borders */
}


        /* Dropdown (select box) */
        div[data-baseweb="select"] > div {
            background-color: #1E1E2F;
            color: white;
            border-radius: 15px;
            border: 4px solid #00CED1;
        }

        /* Slider label color */
        .stSlider label {
            color: #008B8B;
            font-weight: BOLD;
        }

        /* Radio buttons and labels */
        div[role="radiogroup"] label {
            color: #FFFFFF !important;
        }

        /* Form section text */
        .stForm label {
            color: #E0E0E0 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Automatic Diet Recommendation", page_icon="💪",layout="wide")

# 🔹 Custom CSS styling for number inputs and text boxes
# 💡 Custom CSS to make form field headers (Name, Age, etc.) bright and bold
st.markdown("""
<style>
/* 🔹 Make all form labels (Name, Age, Height, etc.) bold and bright */
[data-testid="stForm"] label {
    color: #007BFF !important;    /* Bright ocean blue (you can change below) */
    font-weight: 800 !important;  /* Bold text */
    font-size: 160px !important;   /* Slightly larger */
}

/* 🔹 Optional: make the radio labels (Male/Female) match */
[data-testid="stForm"] div[role="radiogroup"] label {
    color: #007BFF !important;
    font-weight: 700 !important;
}

/* 🔹 Optional: make select and slider labels visible */
[data-testid="stForm"] .stSelectbox label,
[data-testid="stForm"] .stSlider label {
    color: #007BFF !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


dataset=pd.read_csv(r'https://raw.githubusercontent.com/sindhukanumurivs/mealplan/master/recipess.csv')


nutritions_values=['Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent']
# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations=None
    st.session_state.person=None
    st.session_state.weight_loss_option=None
class Person:

    def __init__(self,name,age,height,weight,gender,activity,meals_calories_perc,weight_loss):
        self.name=name
        self.age=age
        self.height=height
        self.weight=weight
        self.gender=gender
        self.activity=activity
        self.meals_calories_perc=meals_calories_perc
        self.weight_loss=weight_loss
    def calculate_bmi(self,):
        bmi=round(self.weight/((self.height/100)**2),2)
        return bmi

    def display_result(self,):
        bmi=self.calculate_bmi()
        bmi_string=f'{bmi} kg/m²'
        if bmi<18.5:
            category='Underweight'
            color='Red'
        elif 18.5<=bmi<25:
            category='Normal'
            color='Green'
        elif 25<=bmi<30:
            category='Overweight'
            color='Yellow'
        else:
            category='Obesity'    
            color='Red'
        return bmi_string,category,color

    def calculate_bmr(self):
        if self.gender=='Male':
            bmr=10*self.weight+6.25*self.height-5*self.age+5
        else:
            bmr=10*self.weight+6.25*self.height-5*self.age-161
        return bmr

    def calories_calculator(self):
        activites=['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights=[1.2,1.375,1.55,1.725,1.9]
        weight = weights[activites.index(self.activity)]
        maintain_calories = self.calculate_bmr()*weight
        return maintain_calories

    def generate_recommendations(self,):
        total_calories=self.weight_loss*self.calories_calculator()
        recommendations=[]
        for meal in self.meals_calories_perc:
            meal_calories=self.meals_calories_perc[meal]*total_calories
            if meal=='breakfast':        
                recommended_nutrition = [meal_calories,rnd(10,30),rnd(0,4),rnd(30,40),rnd(40,60),rnd(40,75),rnd(4,10),rnd(75,80),rnd(0,80)]
            elif meal=='launch':
                recommended_nutrition = [meal_calories,rnd(0,10),rnd(16,25),rnd(26,35),rnd(36,45),rnd(46,55),rnd(56,75),rnd(70,80),rnd(50,75)]
            elif meal=='dinner':
                recommended_nutrition = [meal_calories,rnd(0,30),rnd(0,4),rnd(0,30),rnd(0,90),rnd(40,75),rnd(4,10),rnd(0,10),rnd(30,50)] 
            else:
                recommended_nutrition = [meal_calories,rnd(10,30),rnd(0,4),rnd(0,30),rnd(0,90),rnd(40,75),rnd(4,10),rnd(0,10),rnd(30,50)]
            recommendation_dataframe=recommend(dataset,recommended_nutrition)
            print("$")
            output1=output_recommended_recipes(recommendation_dataframe)
            recommendations.append(output1)
        for recommendation in recommendations:
            for recipe in recommendation:
                recipe['image_link']=find_image(recipe['Name']) 
        return recommendations

class Display:
    def __init__(self):
        self.plans=["Maintain weight","Mild weight loss","Weight loss","Extreme weight loss"]
        self.weights=[1,0.9,0.8,0.6]
        self.losses=['-0 kg/week','-0.25 kg/week','-0.5 kg/week','-1 kg/week']
        pass

    def display_bmi(self,person):
        st.header('BMI CALCULATOR')
        bmi_string,category,color = person.display_result()
        st.metric(label="Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            Healthy BMI range: 18.5 kg/m² - 25 kg/m².
            """)   

    def display_calories(self,person):
        st.header('CALORIES CALCULATOR')        
        maintain_calories=person.calories_calculator()
        st.write('The results show a number of daily calorie estimates that can be used as a guideline for how many calories to consume each day to maintain, lose, or gain weight at a chosen rate.')
        for plan,weight,loss,col in zip(self.plans,self.weights,self.losses,st.columns(4)):
            with col:
                st.metric(label=plan,value=f'{round(maintain_calories*weight)} Calories/day',delta=loss,delta_color="inverse")

    def display_recommendation(self,person,recommendations):
        st.header('DIET RECOMMENDATOR')  
        with st.spinner('Generating recommendations...'): 
            meals=person.meals_calories_perc
            st.subheader('Recommended recipes:')
            for meal_name,column,recommendation in zip(meals,st.columns(len(meals)),recommendations):
                with column:
                    #st.markdown(f'<div style="text-align: center;">{meal_name.upper()}</div>', unsafe_allow_html=True) 
                    st.markdown(f'##### {meal_name.upper()}')    
                    for recipe in recommendation:
                        
                        recipe_name=recipe['Name']
                        expander = st.expander(recipe_name)
                        recipe_link=recipe['image_link']
                        recipe_img=f'<div><center><img src={recipe_link} alt={recipe_name}></center></div>'     
                        nutritions_df=pd.DataFrame({value:[recipe[value]] for value in nutritions_values})      
                        
                        expander.markdown(recipe_img,unsafe_allow_html=True)  
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>', unsafe_allow_html=True)                   
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>', unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"""
                                        - {ingredient}
                            """)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>', unsafe_allow_html=True)    
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"""
                                        - {instruction}
                            """) 
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>', unsafe_allow_html=True)   
                        expander.markdown(f"""
                                - Cook Time       : {recipe['CookTime']}min
                                - Preparation Time: {recipe['PrepTime']}min
                                - Total Time      : {recipe['TotalTime']}min
                            """)                       

    def display_meal_choices(self,person,recommendations):    
        st.subheader('Choose your meal composition:')
        # Display meal compositions choices
        if len(recommendations)==3:
            breakfast_column,launch_column,dinner_column=st.columns(3)
            with breakfast_column:
                breakfast_choice=st.selectbox(f'Choose your breakfast:',[recipe['Name'] for recipe in recommendations[0]])
            with launch_column:
                launch_choice=st.selectbox(f'Choose your launch:',[recipe['Name'] for recipe in recommendations[1]])
            with dinner_column:
                dinner_choice=st.selectbox(f'Choose your dinner:',[recipe['Name'] for recipe in recommendations[2]])  
            choices=[breakfast_choice,launch_choice,dinner_choice]     
        elif len(recommendations)==4:
            breakfast_column,morning_snack,launch_column,dinner_column=st.columns(4)
            with breakfast_column:
                breakfast_choice=st.selectbox(f'Choose your breakfast:',[recipe['Name'] for recipe in recommendations[0]])
            with morning_snack:
                morning_snack=st.selectbox(f'Choose your morning_snack:',[recipe['Name'] for recipe in recommendations[1]])
            with launch_column:
                launch_choice=st.selectbox(f'Choose your launch:',[recipe['Name'] for recipe in recommendations[2]])
            with dinner_column:
                dinner_choice=st.selectbox(f'Choose your dinner:',[recipe['Name'] for recipe in recommendations[3]])
            choices=[breakfast_choice,morning_snack,launch_choice,dinner_choice]                
        else:
            breakfast_column,morning_snack,launch_column,afternoon_snack,dinner_column=st.columns(5)
            with breakfast_column:
                breakfast_choice=st.selectbox(f'Choose your breakfast:',[recipe['Name'] for recipe in recommendations[0]])
            with morning_snack:
                morning_snack=st.selectbox(f'Choose your morning_snack:',[recipe['Name'] for recipe in recommendations[1]])
            with launch_column:
                launch_choice=st.selectbox(f'Choose your launch:',[recipe['Name'] for recipe in recommendations[2]])
            with afternoon_snack:
                afternoon_snack=st.selectbox(f'Choose your afternoon:',[recipe['Name'] for recipe in recommendations[3]])
            with dinner_column:
                dinner_choice=st.selectbox(f'Choose your  dinner:',[recipe['Name'] for recipe in recommendations[4]])
            choices=[breakfast_choice,morning_snack,launch_choice,afternoon_snack,dinner_choice] 
        
        # Calculating the sum of nutritional values of the choosen recipes
        total_nutrition_values={nutrition_value:0 for nutrition_value in nutritions_values}
        chosen_recipes_data = []
        meal_names = list(person.meals_calories_perc.keys())

        for choice, meal_group, meal_name in zip(choices, recommendations, meal_names):
            for meal in meal_group:
                if meal['Name'] == choice:
                    recipe_data = {'Meal': meal_name.capitalize(), 'Name': meal['Name']}
                    for nutrition_value in nutritions_values:
                        recipe_data[nutrition_value] = meal[nutrition_value]
                        total_nutrition_values[nutrition_value] += meal[nutrition_value]
                    chosen_recipes_data.append(recipe_data)

        total_calories_chose=total_nutrition_values['Calories']
        loss_calories_chose=round(person.calories_calculator()*person.weight_loss)

        # Display corresponding graphs
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Total Calories in Recipes vs {st.session_state.weight_loss_option} Calories:</h5>', unsafe_allow_html=True)
        total_calories_graph_options = {
    "xAxis": {
        "type": "category",
        "data": ['Total Calories you chose', f"{st.session_state.weight_loss_option} Calories"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "data": [
                {"value":total_calories_chose, "itemStyle": {"color":["#33FF8D","#FF3333"][total_calories_chose>loss_calories_chose]}},
                {"value": loss_calories_chose, "itemStyle": {"color": "#3339FF"}},
            ],
            "type": "bar",
        }
    ],
}
        st_echarts(options=total_calories_graph_options,height="400px",)
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values:</h5>', unsafe_allow_html=True)
        nutritions_graph_options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "Nutritional Values",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": [{"value":round(total_nutrition_values[total_nutrition_value]),"name":total_nutrition_value} for total_nutrition_value in total_nutrition_values],
        }
    ],
}       
        st_echarts(options=nutritions_graph_options, height="500px",)

        # Export to CSV
        st.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Export Your Meal Plan</h5>', unsafe_allow_html=True)
        
        export_df = pd.DataFrame(chosen_recipes_data)
        
        # Add Totals row
        totals_row = {'Meal': 'Total', 'Name': ''}
        totals_row.update(total_nutrition_values)
        export_df = pd.concat([export_df, pd.DataFrame([totals_row])], ignore_index=True)

        # Reorder columns
        cols = ['Meal', 'Name'] + nutritions_values
        export_df = export_df[cols]

        csv = export_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download Meal Plan as CSV",
            data=csv,
            file_name=f'{person.name.replace(" ", "_")}_diet_plan.csv',
            mime='text/csv',
        )

display=Display()
title="<h1 style='text-align: center; color: #2E8B57;'>Automatic Diet Recommendation</h1>"
st.markdown(title, unsafe_allow_html=True)
with st.form("recommendation_form"):
    st.write("Modify the values and click the Generate button to use")
    name = st.text_input('Name');
    age = st.number_input('Age',min_value=2, max_value=120, step=1)
    height = st.number_input('Height(cm)',min_value=50, max_value=300, step=1)
    weight = st.number_input('Weight(kg)',min_value=10, max_value=300, step=1)
    gender = st.radio('Gender',('Male','Female'))
    activity = st.select_slider('Activity',options=['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 
    'Extra active (very active & physical job)'])
    option = st.selectbox('Choose your weight loss plan:',display.plans)
    st.session_state.weight_loss_option=option
    weight_loss=display.weights[display.plans.index(option)]
    number_of_meals=st.slider('Meals per day',min_value=3,max_value=5,step=1,value=3)
    if number_of_meals==3:
        meals_calories_perc={'breakfast':0.35,'lunch':0.40,'dinner':0.25}
    elif number_of_meals==4:
        meals_calories_perc={'breakfast':0.30,'morning snack':0.05,'lunch':0.40,'dinner':0.25}
    else:
        meals_calories_perc={'breakfast':0.30,'morning snack':0.05,'lunch':0.40,'afternoon snack':0.05,'dinner':0.20}
    generated = st.form_submit_button("Generate")
if generated:
    st.session_state.generated=True
    person = Person(name,age,height,weight,gender,activity,meals_calories_perc,weight_loss)
    with st.container():
        display.display_bmi(person)
    with st.container():
        display.display_calories(person)
    with st.spinner('Generating recommendations...'):     
        recommendations=person.generate_recommendations()
        st.session_state.recommendations=recommendations
        st.session_state.person=person

if st.session_state.generated:
    with st.container():
        display.display_recommendation(st.session_state.person,st.session_state.recommendations)
        st.success('Recommendation Generated Successfully !', icon="✅")
    with st.container():
        display.display_meal_choices(st.session_state.person,st.session_state.recommendations)
