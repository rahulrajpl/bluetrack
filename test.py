from analytics.Analytics import ObluAnalytics

oa = ObluAnalytics(data_path='sensor/GetData/steps.txt')

score = oa.getThresholdScore()

print(score)