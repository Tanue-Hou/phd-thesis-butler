# КЛАСТЕР: ИНФОРМАТИКА И ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ (COMPUTER_AI)

## Обзор

Кластер охватывает компьютерные науки, машинное обучение, глубокое обучение, обработку естественного языка, компьютерное зрение, системное ПО и распределённые системы.

## Дисциплинарные области

### 1. Машинное обучение (Machine Learning)

#### Классические методы
- Линейные модели (регрессия, классификация)
- Деревья решений и ансамбли (Random Forest, XGBoost, LightGBM)
- SVM (Support Vector Machines) — ядра, мультикласс
- Кластеризация (K-Means, DBSCAN, иерархическая)
- Снижение размерности (PCA, t-SNE, UMAP)

#### Глубокое обучение (Deep Learning)
- Свёрточные нейронные сети (CNN) — ResNet, EfficientNet, ConvNeXt
- Рекуррентные сети (RNN, LSTM, GRU)
- Архитектура трансформер (Transformer) — BERT, GPT, ViT
- Generative models: GAN, VAE, Diffusion Models
- Self-supervised и contrastive learning

#### Обучение с подкреплением (Reinforcement Learning)
- Q-Learning, DQN, PPO, SAC, TD3
- Model-based vs Model-free RL
- Multi-agent RL
- Sim-to-real transfer

### 2. Обработка естественного языка (NLP)

- Токенизация, лемматизация, морфологический анализ
- Классификация текстов, сентимент-анализ
- Именованные сущности (NER)
- Машинный перевод
- Вопросно-ответные системы
- RAG (Retrieval-Augmented Generation)
- Fine-tuning LLM, LoRA, prompt engineering

### 3. Компьютерное зрение (Computer Vision)

- Классификация изображений
- Обнаружение объектов (YOLO, DETR)
- Семантическая/инстанс/паноптическая сегментация
- Оценка глубины, Optical Flow
- 3D-реконструкция (NeRF, 3D Gaussian Splatting)
- Video understanding

### 4. Системное ПО и распределённые системы

- Операционные системы, виртуализация
- Распределённые базы данных (CAP-теорема, Paxos, Raft)
- Микросервисная архитектура
- Облачные вычисления, контейнеризация (Docker, Kubernetes)
- Edge computing и IoT

### 5. Безопасность и криптография

- Криптографические протоколы
- Атаки на ML-модели (adversarial attacks, poisoning)
- Дифференциальная приватность
- Federated learning

## Типовая структура диссертации (COMPUTER_AI)

1. Введение (постановка проблемы, мотивация)
2. Обзор существующих подходов
3. Предлагаемый метод/алгоритм/архитектура
4. Теоретический анализ (сложность, сходимость, гарантии)
5. Экспериментальная оценка (датасеты, метрики, бенчмарки)
6. Обсуждение результатов
7. Выводы

## evidence_count

| Элемент | Типичный evidence_count | Уровень |
|---|---|---|
| Сравнение с SOTA | 5–15 baseline-методов | high |
| Датасеты | 2–5 стандартных датасетов | high |
| Ablation study | 3–10 вариантов | medium |
| Статистическая значимость | 3–5 запусков с разными seeds | medium |

## Инструменты

- **Фреймворки**: PyTorch, TensorFlow, JAX
- **Эксперименты**: Weights & Biases, MLflow, ClearML
- **Вычисления**: GPU-кластеры, Google Colab, AWS/GCP
- **Данные**: HuggingFace Datasets, Kaggle
