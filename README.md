# 🏢 Wielka Ucieczka z Więzienia

Interaktywna gra tekstowo-graficzna zrealizowana w języku Python z wykorzystaniem biblioteki graficznej `turtle`. Gracz wciela się w rolę więźnia, którego celem jest przetrwanie w trudnych warunkach, zarządzanie zasobami, unikanie strażników oraz zebranie odpowiednich narzędzi niezbędnych do zaplanowania i wykonania brawurowej ucieczki.

## ⚙️ Zaawansowany System Poziomów Trudności

Gra posiada dynamicznie skalowany poziom wyzwania wybierany na samym początku rozgrywki. Wpływa on bezpośrednio na ekonomię, mechanikę skradania, system minigier oraz unikalne ograniczenia biologiczne bohatera:

| Cecha gry | 🟢 Łatwy | 🟡 Średni | 🔴 Trudny |
| :---        |    :----:   |          ---: |
| **Próby przy szafkach** | **10 prób** (Brak pośpiechu) | **5 prób** (Zbalansowane) | **3 próby** (Wysokie ryzyko) |
| **Zasięg kamer** | Mały (promień 10) | Standardowy (promień 15) | Olbrzymi (promień 25) |
| **Szansa na ucieczkę/atak** | Bonus **+25%** do szans | Standardowe szanse | Kara **-15%** do szans |
| **Ceny u Cinkciarza** | Taniej o 1 pączek | Standardowe ceny | Drożej o 1 pączek |
| **Limit snu na dobę** | Bez limitu | Bez limitu | **Maksymalnie 2 sny na dobę** |
## 🔋 Mechanika Energii i Głodu

Życie więźnia opisują dwa kluczowe wskaźniki, które decydują o sukcesie podejmowanych działań:

* **Głód (0-100%):** Spada z każdym krokiem poza celą. Osiągnięcie wartości `0%` skutkuje natychmiastowym omdleniem i końcem gry (śmierć głodowa). Posiłki można znajdować w szafkach i spożywać z poziomu ekwipunku.
* **Energia (0-100%):** Zużywa się podczas eksploracji korytarzy oraz gwałtownych akcji (ucieczka przed strażnikiem zabiera 30 energii, walka kijem 20). Jeśli poziom energii spadnie poniżej 50%, szanse na obronę przed strażą drastycznie maleją.
* **Regeneracja (Sen):** Odpoczynek na pryczy trwa 6 godzin w grze i w pełni odnawia Energię (kosztem 15% głodu). Na poziomie **Trudnym** mechanizm ten symuluje bezsenność – po drugim spaniu w ciągu tej samej doby gracz nie będzie mógł zasnąć aż do kolejnego dnia.

## 🎮 Główne Funkcje i Elementy Rozgrywki

1. **System Cyklu Dobowego:** Czas w grze płynie z każdą turą. W godzinach nocnych (22:00 – 06:00) czujność strażników spada, co ułatwia przemieszczanie się.
2. **Kamery Monitoringu:** Losowo rozmieszczane na mapie obszary detekcji. Wejście w pole widzenia kamery w ciągu dnia natychmiastowo uruchamia alarm i ściąga strażnika.
3. **Skalowana Mini-gra (Lockpicking):** Włamywanie się do szafek opiera się na losowaniu typu skrytki (od drewnianej komody po elektroniczny sejf) oraz odgadywaniu szyfru. Liczba szans zależy bezpośrednio od wybranego poziomu trudności (10 / 5 / 3).
4. **Czarny Rynek (Handlarz Cinkciarz):** Możliwość wymiany znalezionych pączków na kluczowe przedmioty fabularne. Ceny są modyfikowane przez poziom trudności.
5. **System Logowania Wyników:** Każda gra automatycznie generuje lub dopisuje podsumowanie (data, poziom trudności, czas ucieczki, liczba tur, status) do pliku tekstowego `historia_ucieczek.txt`.

## 🕹️ Instrukcja Obsługi i Sterowania

Rozgrywka odbywa się w turach. W konsoli co turę wyświetlane jest menu wyboru akcji:
* **`1` (Ruch):** Pozwala przemieścić żółwia na planszy graficznej. Należy podać odległość kroku (1-10) oraz kąt obrotu (kierunek).
* **`2` (Ekwipunek):** Otwiera plecak z podziałem na kategorie (Jedzenie, Ucieczka, Inne), umożliwiając zarządzanie przedmiotami i jedzenie.
* **`3` (Akcja kontekstowa):** W zależności od miejsca pozwala wyjść na korytarz, bezpiecznie wrócić na pryczę lub zainicjować finalną ucieczkę (wymaga posiadania Pilniczka, Liny i Spadochronu w celi).
* **`4` (Poddaj się):** Natychmiastowa rezygnacja i kapitulacja.
* **`5` (Idź spać):** Opcja regeneracji energii dostępna tylko wewnątrz celi.

### 🖥️ Prawidłowe Zamknięcie Gry
Po wygranej, przegranej lub kapitulacji gra generuje pełne statystyki końcowe. Aby bezpiecznie zamknąć aplikację i zamknąć proces, należy **kliknąć raz lewym przyciskiem myszy w dowolnym miejscu okna graficznego Turtle**.
