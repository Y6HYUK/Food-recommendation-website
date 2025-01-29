import random
from flask import Flask, render_template, request
import json

app = Flask(__name__)

def load_food_data():
    with open('/home/yjh/junhyuk_project/eat_web_ws/food_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

food_data = load_food_data()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        mood = request.form.get('mood')
        weather = request.form.get('weather')
        company = request.form.get('company')
        meal_type = request.form.get('meal_type')
        cuisine = request.form.get('cuisine')

        # 추천 로직
        recommendation, reason = get_recommendation(mood, weather, company, meal_type, cuisine)

        return render_template('result.html',
                               mood=mood,
                               weather=weather,
                               company=company,
                               meal_type=meal_type,
                               cuisine=cuisine,
                               recommendation=recommendation,
                               reason=reason)
    return render_template('index.html')

def get_recommendation(mood, weather, company, meal_type, cuisine):
    # 조건에 맞는 음식 필터링
    filtered_foods = food_data

    # 조건별 필터링, "선택안함"인 경우 무시
    if cuisine and cuisine != "선택안함":
        filtered_foods = [food for food in filtered_foods if food['cuisine'] == cuisine]
    
    if meal_type and meal_type != "선택안함":
        filtered_foods = [food for food in filtered_foods if food['meal_type'] == meal_type]
    
    if mood and mood != "선택안함":
        filtered_foods = [food for food in filtered_foods if mood in food['suitable_mood']]
    
    if weather and weather != "선택안함":
        filtered_foods = [food for food in filtered_foods if weather in food['suitable_weather']]
    
    if company and company != "선택안함":
        filtered_foods = [food for food in filtered_foods if company in food['suitable_company']]

    if filtered_foods:
        # 조건에 맞는 음식 중 하나 랜덤 선택
        selected_food = random.choice(filtered_foods)
        recommendation = selected_food['name']
        reason = selected_food['reason']
    else:
        # 조건에 맞는 음식이 없을 경우, 전체 음식 중 3~5개 랜덤 선택
        fallback_recommendations = random.sample(food_data, min(5, len(food_data)))
        recommendation = [food['name'] for food in fallback_recommendations]
        reason = "조건에 맞는 음식이 없어, 다음 중 하나를 선택해서 드셔보세요."

    return recommendation, reason

if __name__ == '__main__':
    app.run(debug=True)
