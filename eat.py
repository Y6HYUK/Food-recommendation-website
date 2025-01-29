from flask import Flask, render_template, request
import random
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
        recommendation, reason, narrative = get_recommendation(mood, weather, company, meal_type, cuisine)

        return render_template('result.html',
                               recommendation=recommendation,
                               reason=reason,
                               narrative=narrative)
    return render_template('index.html')

def get_recommendation(mood, weather, company, meal_type, cuisine):
    # 선택된 조건들을 딕셔너리에 저장 (선택안함 제외)
    selected_conditions = {
        'cuisine': cuisine if cuisine and cuisine != "선택안함" else None,
        'meal_type': meal_type if meal_type and meal_type != "선택안함" else None,
        'mood': mood if mood and mood != "선택안함" else None,
        'weather': weather if weather and weather != "선택안함" else None,
        'company': company if company and company != "선택안함" else None
    }

    # 내러티브 생성
    selected_texts = []
    for key, value in selected_conditions.items():
        if value:
            if key == 'cuisine':
                selected_texts.append(f"음식 종류는 {value}을(를) 선택하셨습니다.")
            elif key == 'meal_type':
                selected_texts.append(f"식사 유형으로는 {value}을(를) 선택하셨습니다.")
            elif key == 'mood':
                selected_texts.append(f"오늘의 기분은 {value}이시군요.")
            elif key == 'weather':
                selected_texts.append(f"오늘 날씨는 {value}입니다.")
            elif key == 'company':
                selected_texts.append(f"함께하는 사람은 {value}이시군요.")

    if selected_texts:
        narrative = " ".join(selected_texts)
    else:
        narrative = "오늘의 상황에 맞는 음식을 추천해드릴게요."

    # Scoring system: 각 음식이 몇 개의 조건을 만족하는지 계산
    scored_foods = []
    for food in food_data:
        score = 0
        if selected_conditions['cuisine'] and food.get('cuisine') == selected_conditions['cuisine']:
            score += 1
        if selected_conditions['meal_type'] and food.get('meal_type') == selected_conditions['meal_type']:
            score += 1
        if selected_conditions['mood'] and selected_conditions['mood'] in food.get('suitable_mood', []):
            score += 1
        if selected_conditions['weather'] and selected_conditions['weather'] in food.get('suitable_weather', []):
            score += 1
        if selected_conditions['company'] and selected_conditions['company'] in food.get('suitable_company', []):
            score += 1
        scored_foods.append((food, score))

    # 최대 점수 찾기
    max_score = max(score for (food, score) in scored_foods) if scored_foods else 0

    if max_score > 0:
        # 최대 점수를 가진 음식들 추출
        top_foods = [food for (food, score) in scored_foods if score == max_score]
        # 랜덤으로 하나 선택
        selected_food = random.choice(top_foods)
        recommendation = selected_food['name']
        reason = selected_food.get('reason', '당신의 선택에 맞는 음식입니다.')
    else:
        # 조건에 맞는 음식이 없을 경우, 대안으로 3~5개의 랜덤 음식 추천
        num_recommendations = min(5, len(food_data))
        fallback_recommendations = random.sample(food_data, num_recommendations)
        recommendation = [food['name'] for food in fallback_recommendations]
        reason = "조건에 맞는 음식이 없어, 다음 중 하나를 선택해보세요."

    # 추천 이유를 분석적인 문장으로 변환
    if isinstance(recommendation, str):
        reason = f"{reason}"
    else:
        reason = f"{reason}"

    return recommendation, reason, narrative

if __name__ == '__main__':
    app.run(debug=True)
