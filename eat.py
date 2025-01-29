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
        recommendation, reason, selected_conditions = get_recommendation(mood, weather, company, meal_type, cuisine)

        return render_template('result.html',
                               recommendation=recommendation,
                               reason=reason,
                               selected_conditions=selected_conditions)
    return render_template('index.html')

def get_recommendation(mood, weather, company, meal_type, cuisine):
    # 선택된 조건들을 딕셔너리에 저장 (선택안함 제외)
    selected_conditions = {
        '식사 유형': meal_type if meal_type and meal_type != "선택안함" else None,
        '음식 종류': cuisine if cuisine and cuisine != "선택안함" else None,
        '기분': mood if mood and mood != "선택안함" else None,
        '날씨': weather if weather and weather != "선택안함" else None,
        '함께하는 사람': company if company and company != "선택안함" else None
    }

    # 내러티브 생성을 위한 리스트 (현재 사용하지 않음)
    selected_texts = []
    for key, value in selected_conditions.items():
        if value:
            if key == '음식 종류':
                selected_texts.append(f"{key}은(는) {value}을(를) 선택하셨습니다.")
            elif key == '식사 유형':
                selected_texts.append(f"{key}으로 {value}을(를) 선택하셨습니다.")
            else:
                selected_texts.append(f"오늘의 {key.lower()}는 {value}입니다.")

    if selected_texts:
        narrative = " ".join(selected_texts)
    else:
        narrative = "오늘의 상황에 맞는 음식을 추천해드릴게요."

    # Scoring system: 각 음식이 몇 개의 조건을 만족하는지 계산
    scored_foods = []
    for food in food_data:
        score = 0
        if selected_conditions['음식 종류'] and food.get('cuisine') == selected_conditions['음식 종류']:
            score += 1
        if selected_conditions['식사 유형'] and food.get('meal_type') == selected_conditions['식사 유형']:
            score += 1
        if selected_conditions['기분'] and selected_conditions['기분'] in food.get('suitable_mood', []):
            score += 1
        if selected_conditions['날씨'] and selected_conditions['날씨'] in food.get('suitable_weather', []):
            score += 1
        if selected_conditions['함께하는 사람'] and selected_conditions['함께하는 사람'] in food.get('suitable_company', []):
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

    return recommendation, reason, selected_conditions

if __name__ == '__main__':
    app.run(debug=True)
