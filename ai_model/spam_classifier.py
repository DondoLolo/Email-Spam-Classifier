import pandas as pd

df = pd.read_csv('training_emails.csv')
df['text'] = (
    df['Subject'].fillna("")+ " "+
    df['Sender'].fillna("")+ " "+
    df['Body'].fillna("")
)
X = df['text']
y = df['Spam']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.2, random_state=42)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_train_vectors = vectorizer.fit_transform(X_train)
X_test_vectors = vectorizer.transform(X_test)

from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train_vectors, y_train)

from sklearn.metrics import accuracy_score
predictions = model.predict(X_test_vectors)
accuracy = accuracy_score(y_test, predictions)
print(accuracy)

