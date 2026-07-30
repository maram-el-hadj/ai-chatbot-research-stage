# Benchmark : Pure Python vs LangChain

Ce document résume les différences clés entre l'utilisation de **Python pur** et **LangChain** pour la gestion des prompts.

---

## 📊 Tableau Comparatif

| Critère | Pure Python | LangChain |
| :--- | :--- | :--- |
| **Création de prompt** | Manual prompt | PromptTemplate |
| **Formatage** | String formatting (`f-strings`) | Reusable templates |
| **Structure** | Less structured | More modular |

---

## 🎯 Conclusion de l'expérience

* **Pure Python :** Pratique et rapide pour de très petits scripts simples, mais devient chaotique dès que la complexité augmente.
* **LangChain :** Offre une structure modulaire et réutilisable qui facilite l'assemblage de prompts complexes avant de les envoyer aux LLMs.