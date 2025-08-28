
# 📦 Modèle de Données — Dashboard SaaS pour SIB

Ce fichier contient la **liste complète des tables** nécessaires pour développer le dashboard SaaS décrit dans le cahier des charges de SIB.

---

## 🔒 1. `users` (Utilisateurs)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| name             | VARCHAR                                |
| email            | VARCHAR (UNIQUE)                       |
| password_hash    | VARCHAR                                |
| role             | ENUM('commercial', 'magasin', 'production', 'admin') |
| created_at       | TIMESTAMP                              |

---

## 🏗 2. `materials` (Matières Premières)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| name             | VARCHAR                                |
| reference_code   | VARCHAR (UNIQUE)                       |
| unit             | VARCHAR (ex: kg, tonne)                |
| description      | TEXT                                   |
| created_at       | TIMESTAMP                              |

---

## 🏭 3. `semi_finished_products` (Produits Semi-Finis)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| name             | VARCHAR                                |
| reference_code   | VARCHAR (UNIQUE)                       |
| description      | TEXT                                   |
| created_at       | TIMESTAMP                              |

---

## 📦 4. `finished_products` (Produits Finis)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| name             | VARCHAR                                |
| reference_code   | VARCHAR (UNIQUE)                       |
| description      | TEXT                                   |
| created_at       | TIMESTAMP                              |

---

## 📊 5. `stock` (Stock Global)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| item_type        | ENUM('material', 'semi_finished', 'finished') |
| item_id          | INT (FK vers la table correspondante)  |
| quantity         | DECIMAL                                |
| location         | VARCHAR                                |
| last_updated     | TIMESTAMP                              |

---

## 👥 6. `clients` (Clients)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| company_name     | VARCHAR                                |
| contact_person   | VARCHAR                                |
| email            | VARCHAR                                |
| phone            | VARCHAR                                |
| address          | TEXT                                   |

---

## 📦 7. `orders` (Commandes)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| client_id        | INT (FK vers `clients`)                |
| status           | ENUM('pending', 'in_production', 'shipped', 'delivered', 'cancelled') |
| order_date       | DATE                                   |
| delivery_date    | DATE                                   |
| created_by       | INT (FK vers `users`)                  |
| created_at       | TIMESTAMP                              |

---

## 🧾 8. `order_items` (Articles de Commande)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| order_id         | INT (FK vers `orders`)                 |
| product_id       | INT (FK vers `finished_products`)      |
| quantity         | DECIMAL                                |
| unit_price       | DECIMAL                                |

---

## ⚙️ 9. `production` (Suivi Production)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| product_id       | INT (FK vers `semi_finished_products` ou `finished_products`) |
| quantity_planned | DECIMAL                                |
| quantity_produced| DECIMAL                                |
| start_date       | DATE                                   |
| end_date         | DATE                                   |
| status           | ENUM('planned', 'in_progress', 'completed') |
| created_by       | INT (FK vers `users`)                  |

---

## 🧪 10. `production_materials` (Matières Utilisées)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| production_id    | INT (FK vers `production`)             |
| material_id      | INT (FK vers `materials`)              |
| quantity_used    | DECIMAL                                |

---

## 📧 11. `messages` (Messages Internes)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| sender_id        | INT (FK vers `users`)                  |
| receiver_id      | INT (FK vers `users`)                  |
| message          | TEXT                                   |
| created_at       | TIMESTAMP                              |
| read_status      | BOOLEAN                                |

---

## 📚 12. `activity_logs` (Historique des Activités)

| Champ             | Type                                   |
|------------------|----------------------------------------|
| id               | INT (PK)                               |
| user_id          | INT (FK vers `users`)                  |
| action           | VARCHAR                                |
| entity_type      | VARCHAR (ex: 'stock', 'order')         |
| entity_id        | INT                                    |
| timestamp        | TIMESTAMP                              |
| details          | TEXT                                   |
