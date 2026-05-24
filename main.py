import random
import turtle
from datetime import datetime

# Kolorki do konsoli - skrócone nazwy zmiennych, mniej szablonowo
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_CHRONO = "\033[35m"
C_CYAN = "\033[36m"

gd = True # flaga glowna pętli

# słownik z wartościami jedzenia
statystyki = {
    "Suchy Chleb": 5,
    "Ciastko": 10,
    "Jabłko": 20,
    "Suchy Makaron": 15,
    "Pączek": 30
}

class Wiezien: # zmienione z User na bardziej pasujące do gry
    def __init__(self):
        # moj ekwipunek podręczny
        self.plecak = {
            "Jedzenie": ["Suchy Chleb"],
            "Ucieczka": ["Pilniczek"],
            "Inne": []
        }

        self.hp_brzuch = 100 # poziom głodu
        self.stamina = 100    # energia ziomka
        self.diff = 2         # poziom trudnosci domyslny
        self.diff_txt = "Średni"

        self.max_proby = 5
        self.cam_r = 15
        self.bonus_szans = 0
        self.cena_mod = 0

        self.sleep_cnt = 0
        self.last_sleep_day = 1

        # logi akcji
        self.akcje_log = {
            "Przesuniecia": [],
            "Akcje": ["Pusto"]
        }

        self.ruchy_cnt = 0
        self.w_celi = True
        self.ostatni_dystans = 0
        self.ostatni_kat = 0

        # czas gry
        self.godz = 8
        self.min_nr = 0
        self.dzien_nr = 1

        # inicjalizacja okna turtle
        self.wn = turtle.Screen()
        self.wn.bgcolor("#2c3e50")
        self.wn.title("Wielka Ucieczka z Więzienia - v3.5 - REWORK")

        self.t = turtle.Turtle()
        self.t.speed(0)
        self.t.pensize(2)

        # interfejs / naglowek
        self.h = turtle.Turtle()
        self.h.speed(0)
        self.h.ht()
        self.h.pu()
        self.h.color("white")

        self.X = 0
        self.Y = 0
        self.strefy_kamer = []

    def wybierz_poziom(self):
        print(f"\n{C_BOLD}{C_BLUE}=== WYBÓR POZIOMU TRUDNOŚCI ==={C_RESET}")
        print(f" 1. {C_GREEN}Łatwy{C_RESET}   (10 prób na szafki, +25% szans na ucieczkę, tańszy handel, sen bez limitu)")
        print(f" 2. {C_YELLOW}Średni{C_RESET}  (5 prób na szafki, zbalansowana rozgrywka)")
        print(f" 3. {C_RED}Trudny{C_RESET}  (3 próby na szafki, -15% szans na ucieczkę, droższy handel, max 2 sny na dobę!)")
        print(f"{C_BLUE}================================{C_RESET}")

        while True:
            odp = input(f"{C_YELLOW}Wybierz poziom (1-3) >>> {C_RESET}").strip()
            if odp in ["1", "2", "3"]: 
                break
            print(f"{C_RED}Błędny klawisz! Wpisz 1, 2 lub 3!{C_RESET}")

        if odp == "1":
            self.diff = 1
            self.diff_txt = "Łatwy"
            self.max_proby = 10
            self.cam_r = 10
            self.bonus_szans = 25
            self.cena_mod = -1
        elif odp == "2":
            self.diff = 2
            self.diff_txt = "Średni"
            self.max_proby = 5
            self.cam_r = 15
            self.bonus_szans = 0
            self.cena_mod = 0
        else:
            self.diff = 3
            self.diff_txt = "Trudny"
            self.max_proby = 3
            self.cam_r = 25
            self.bonus_szans = -15
            self.cena_mod = 1

    @property
    def pobierzCzas(self):
        return f"Dzień {self.dzien_nr}, {str(self.godz).zfill(2)}:{str(self.min_nr).zfill(2)}"

    def uplyw_czasu(self):
        # czas leci co pol godziny po kazdej akcji
        self.min_nr += 30
        if self.min_nr >= 60:
            self.min_nr = 0
            self.godz += 1
        if self.godz >= 24:
            self.godz = 0
            self.dzien_nr += 1

    def odswiezHud(self):
        self.h.clear()
        self.h.goto(-self.map_w / 2 + 10, self.map_h / 2 + 10)
        loc_status = "W CELI" if self.w_celi else "ZAGROŻENIE"
        self.h.write(
            f"{self.pobierzCzas} | Trudność: {self.diff_txt} | Głód: {self.hp_brzuch}% | Energia: {self.stamina}% | Status: {loc_status}",
            font=("Arial", 10, "bold")
        )

    def generuj_mape(self, w, h):
        self.map_w = w
        self.map_h = h
        print(f"{C_CYAN}Rysowanie geometrii wiezienia przy uzyciu Turtle...{C_RESET}")

        self.t.pu()
        self.t.goto(-w / 2, -h / 2)
        self.t.pd()

        # wyznaczanie koordynatów celi startowej
        self.c_xmin = -w / 2
        self.c_xmax = -w / 2 + w / 10
        self.c_ymax = h / 2
        self.c_ymin = h / 2 - h / 10

        self.t.color("#ecf0f1")
        for _ in range(2):
            self.t.forward(w)
            self.t.left(90)
            self.t.forward(h)
            self.t.left(90)

        # rysowanie celi czerwonym kolorem
        self.t.pu()
        self.t.goto(self.c_xmin, self.c_ymin)
        self.t.setheading(0)
        self.t.pd()
        self.t.color("#e74c3c")
        for _ in range(2):
            self.t.forward(self.c_xmax - self.c_xmin)
            self.t.left(90)
            self.t.forward(self.c_ymax - self.c_ymin)
            self.t.left(90)

        # wrzucenie losowych kamer monitoringowych
        for _ in range(3):
            kx = random.randint(int(-w / 2 + w / 5), int(w / 2 - 20))
            ky = random.randint(int(-h / 2 + 20), int(h / 2 - h / 5))
            self.strefy_kamer.append((kx, ky))
            self.t.pu()
            self.t.goto(kx, ky)
            self.t.pd()
            self.t.color("#95a5a6")
            self.t.circle(self.cam_r)

        # ustawienie gracza na srodku celi
        self.t.pu()
        srodek_x = self.c_xmin + (self.c_xmax - self.c_xmin) / 2
        srodek_y = self.c_ymin + (self.c_ymax - self.c_ymin) / 2
        self.t.goto(srodek_x, srodek_y)
        self.t.setheading(90)

        self.t.shape("turtle")
        self.t.color("#2ecc71")

        self.X = self.t.xcor()
        self.Y = self.t.ycor()
        self.ostatni_kat = self.t.heading()
        self.odswiezHud()

    def przemieszczenie(self, d_in, k_in):
        # typowo ludzka walidacja błędów - jak coś padnie, ustawiamy wartości domyślne
        try:
            dist = int(d_in)
            if dist < 1 or dist > 10:
                print(f"{C_RED}[!] Krok musi być między 1 a 10. Ustawiam domyślnie 5.{C_RESET}")
                dist = 5
        except ValueError:
            print(f"{C_RED}[!] Zły format liczby, idziesz o 1 jednostkę.{C_RESET}")
            dist = 1

        try:
            angle = int(k_in)
        except ValueError:
            print(f"{C_RED}[!] Zły kąt, idziesz na wprost (0 stopni).{C_RESET}")
            angle = 0

        self.ostatni_dystans = dist
        self.ostatni_kat = angle

        self.t.setheading(angle)
        self.t.forward(dist)
        self.uplyw_czasu()

        self.X = self.t.xcor()
        self.Y = self.t.ycor()

        lim_x = self.map_w / 2
        lim_y = self.map_h / 2

        # Sprawdzenie płotu zewnętrznego
        if self.X > lim_x or self.X < -lim_x or self.Y > lim_y or self.Y < -lim_y:
            print(f"{C_RED}\n[!] Łooo panie! Wyszedłeś poza mapę! Strażnicy ściągają Cię z ogrodzenia!{C_RESET}")
            self.w_celi = True
            sx = self.c_xmin + (self.c_xmax - self.c_xmin) / 2
            sy = self.c_ymin + (self.c_ymax - self.c_ymin) / 2
            self.t.goto(sx, sy)
            self.t.setheading(90)
            self.X = self.t.xcor()
            self.Y = self.t.ycor()
            self.ruchy_cnt += 1
            self.akcje_log["Przesuniecia"].append([dist, angle])
        else:
            w_celi_nowa = (self.c_xmin <= self.X <= self.c_xmax and self.c_ymin <= self.Y <= self.c_ymax)

            if self.w_celi and not w_celi_nowa:
                self.w_celi = False
            elif (not self.w_celi) and w_celi_nowa:
                self.w_celi = True
            elif (not self.w_celi) and (not w_celi_nowa):
                # spadek statystyk w trakcie spacerowania po korytarzach
                self.hp_brzuch -= random.choice([4, 5, 6])
                self.stamina -= random.randint(2, 4)
                if self.hp_brzuch < 0: self.hp_brzuch = 0
                if self.stamina < 0: self.stamina = 0

            self.ruchy_cnt += 1
            self.akcje_log["Przesuniecia"].append([dist, angle])

        self.t.setheading(90)
        self.check_kamery()
        self.wylosujZdarzenie()
        self.odswiezHud()

    def check_kamery(self):
        noc = self.godz >= 22 or self.godz < 6
        if noc or self.w_celi: 
            return

        for kx, ky in self.strefy_kamer:
            # odleglosc euklidesowa bez skomplikowanych bibliotek
            odl = ( ( self.X - kx )**2 + ( self.Y - ky )**2 )**0.5
            if odl <= self.cam_r:
                print(f"{C_RED}\n[!] WPADKA! Wszedłeś w pole widzenia kamery! Wyje alarm!{C_RESET}")
                self.t.dot(10, "#e74c3c")
                self.straznik_alert(wymuszone=True)
                break

    def printStatus(self):
        print(f"\n{C_BOLD}{C_BLUE}=" * 35)
        print(f" STATUS WIĘŹNIA | TURA NR {self.ruchy_cnt}")
        print(f"=" * 35 + C_RESET)
        print(f"{C_CHRONO} Pozycja:      {C_RESET}{round(self.X, 2)}, {round(self.Y, 2)}")
        print(f"{C_CHRONO} Ruch:         {C_RESET}o {self.ostatni_dystans} na kąt {self.ostatni_kat}°")
        print(f"{C_CYAN} Czas gry:     {C_RESET}{self.pobierzCzas}")
        print(f"{C_YELLOW} Głód:         {C_RESET}{self.hp_brzuch}/100")
        print(f"{C_CYAN} Energia:      {C_RESET}{self.stamina}/100")
        
        status_celi = f"{C_GREEN}W celi (Bezpieczny){C_RESET}" if self.w_celi else f"{C_RED}Poza celą (Ryzyko){C_RESET}"
        print(f" Status:       {status_celi}")
        print(f" Ostatnia Akcja: {C_BOLD}{self.akcje_log['Akcje'][-1]}{C_RESET}")
        print(f"{C_BLUE}=" * 35 + C_RESET)

    def wylosujZdarzenie(self):
        pula = ["Policjant zauważył cię", "Znalazłeś szafkę z rzeczami", "Pusto", "Spotkałeś Handlarza"]
        szansa = random.randint(0, 99)

        noc = self.godz >= 22 or self.godz < 6
        rate_straznik = 5 if noc else 15

        if szansa <= rate_straznik:
            ev = pula[0]
        elif szansa <= rate_straznik + 25:
            ev = pula[1]
            self.t.dot(6, "#3498db")
        elif szansa <= rate_straznik + 35:
            ev = pula[3]
            self.t.dot(8, "#f1c40f")
        else:
            ev = pula[2]

        self.akcje_log["Akcje"].append(ev)

    def menu_wyboru(self):
        global gd
        print(f"\n{C_BOLD}{C_YELLOW}***** MENU OPCJI *****{C_RESET}")
        print(" 1. Przejdź dalej (Ruch)")
        print(" 2. Przeglądaj Ekwipunek / Użyj")

        win_condition = "Pilniczek" in self.plecak["Ucieczka"] and "Lina" in self.plecak["Ucieczka"] and "Spadochron" in self.plecak["Ucieczka"]

        if self.w_celi and win_condition:
            print(f" 3. {C_GREEN}{C_BOLD}UCIEKNIJ Z WIĘZIENIA! (Masz plan i narzędzia){C_RESET}")
        elif self.w_celi:
            print(" 3. Wyjdź na korytarz / 5. Idź spać")
        else:
            print(" 3. Wróć natychmiast do celi")

        print(f" 4. {C_RED}Poddaj się (Koniec gry){C_RESET}")
        print(f"{C_YELLOW}***********************{C_RESET}")

        while True:
            a = input(f"{C_BOLD}Wybierz działanie >>> {C_RESET}").strip()
            if a in ["1", "2", "3", "4", "5"]: 
                break
            print("Nie ma takiej opcji, wpisz liczbę 1-5!")

        opcja = int(a)
        if opcja == 1 or opcja == 2: 
            return opcja

        if opcja == 3:
            if self.w_celi and win_condition:
                self.koniecGryEkran(sukces=True)
                gd = False
                return 3

            if self.w_celi:
                self.w_celi = False
                kx = self.c_xmin + (self.c_xmax - self.c_xmin) / 2
                ky = self.c_ymin
                self.t.goto(kx, ky)
                print(f"{C_GREEN}Wślizgnąłeś się na ciemny korytarz...{C_RESET}")
            else:
                self.w_celi = True
                sx = self.c_xmin + (self.c_xmax - self.c_xmin) / 2
                sy = self.c_ymin + (self.c_ymax - self.c_ymin) / 2
                self.t.goto(sx, sy)
                print(f"{C_YELLOW}Wróciłeś bezpiecznie na swoją pryczę.{C_RESET}")

            self.X = self.t.xcor()
            self.Y = self.t.ycor()
            self.t.setheading(90)
            self.odswiezHud()
            return 3

        if opcja == 4:
            self.koniecGryEkran(sukces=False)
            gd = False
            return 4

        if opcja == 5 and self.w_celi:
            if self.diff == 3:
                if self.dzien_nr != self.last_sleep_day:
                    self.sleep_cnt = 0
                    self.last_sleep_day = self.dzien_nr

                if self.sleep_cnt >= 2:
                    print(f"{C_RED}[!] Bezsenność! Śpałeś już 2 razy dzisiaj. Nie możesz zasnąć!{C_RESET}")
                    return 5

                self.sleep_cnt += 1
                print(f"{C_RED}[LIMIT TRUDNOŚCI] To Twój {self.sleep_cnt}/2 sen dzisiejszego dnia!{C_RESET}")

            print(f"{C_GREEN}Kładziesz się spać na około 6 godzin...{C_RESET}")
            for _ in range(12): 
                self.uplyw_czasu()

            self.stamina = 100
            self.hp_brzuch = max(0, self.hp_brzuch - 15)

            self.printStatus()
            self.odswiezHud()
            return 5

    def loguj_wynik(self, wynik_gry):
        # bezpieczny zapis pliku z obsługa błędu krytycznego
        teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("historia_ucieczek.txt", "a", encoding="utf-8") as f:
                f.write(f"[{teraz}] Poziom: {self.diff_txt} | Status: {wynik_gry} | Tury: {self.ruchy_cnt} | Czas: {self.pobierzCzas}\n")
            print(f"{C_CYAN}[*] Zapisano statystyki do pliku 'historia_ucieczek.txt'{C_RESET}")
        except IOError:
            print(f"{C_RED}[!] Błąd krytyczny: Brak uprawnień do zapisu pliku historii!{C_RESET}")

    def koniecGryEkran(self, sukces):
        print("\n" + f"{C_BOLD}=" * 45)
        if sukces:
            print(f"{C_GREEN} 🎉 !!! KONGRA-TULACJE !!! 🎉 {C_RESET}")
            print(f"{C_GREEN}Rozpiłowałeś kraty, wspiąłeś się po linie i skoczyłeś ze spadochronem!{C_RESET}")
            print(f"{C_BOLD}{C_GREEN}JESTEŚ WOLNYM CZŁOWIEKIEM!{C_RESET}")
            skutek = "SUKCES (WOLNOSC)"
        else:
            print(f"{C_RED} 👮 PODDAŁEŚ SIĘ! 👮 {C_RESET}")
            print(f"{C_RED}Rzuciłeś narzędzia na ziemię. Strażnicy pakują Cię do izolatki.{C_RESET}")
            skutek = "PORAZKA (PODDANIE)"

        print(f"=" * 45 + C_RESET)
        print(f" Poziom wyzwania: {C_YELLOW}{self.diff_txt}{C_RESET}")
        print(f" Czas ucieczki:   {C_CYAN}{self.pobierzCzas}{C_RESET}")
        print(f" Przetrwane tury:  {self.ruchy_cnt}")
        print(f" Stan głodu:      {self.hp_brzuch}/100")
        print(f"=" * 45 + "\n")
        self.loguj_wynik(skutek)

    def zarzadzaj_eq(self):
        print(f"\n{C_BLUE}--- KIESZENIE W PLECAKU ---{C_RESET}")
        kategorie = list(self.plecak.keys())
        for idx, kat in enumerate(kategorie, 1):
            print(f" {idx}. {kat} ({len(self.plecak[kat])} szt.)")
        print(f" {C_RED}Q. Schowaj plecak{C_RESET}")

        a = input(f"{C_YELLOW}Wybierz index kategorii >>> {C_RESET}").strip()
        if a.lower() == 'q': 
            return "Q"
        if a not in ["1", "2", "3"]: 
            return None

        kat_nazwa = kategorie[int(a) - 1]
        lista_przedmiotow = self.plecak[kat_nazwa]

        if not lista_przedmiotow:
            print(f"{C_RED}Ta sekcja plecaka świeci pustkami!{C_RESET}")
            return None

        print(f"\n{C_BLUE}--- PRZEDMIOTY: {kat_nazwa.upper()} ---{C_RESET}")
        for idx, przedm in enumerate(lista_przedmiotow, 1):
            print(f" {idx}. {przedm}")
        print(f" {C_RED}Q. Wróć wyżej{C_RESET}")

        wybor = input(f"{C_YELLOW}Wybierz przedmiot z listy >>> {C_RESET}").strip()
        if wybor.lower() == 'q': 
            return None

        try:
            indeks = int(wybor) - 1
            if 0 <= indeks < len(lista_przedmiotow):
                return lista_przedmiotow[indeks]
        except ValueError:
            pass
        return None

    def skonsumuj(self, typ):
        if typ in statystyki:
            bonus = statystyki[typ]
            self.hp_brzuch = min(100, self.hp_brzuch + bonus)
            self.plecak["Jedzenie"].remove(typ)
            print(f"{C_GREEN}[*] Zjadłeś {typ}! Poziom głodu: +{bonus}!{C_RESET}")
            self.akcje_log["Akcje"].append(f"Zjedzono {typ}")

    def miniGraZamek(self):
        szafki_opisy = [
            "Stara drewniana komoda z prostą kłódką kłapiącą",
            "Zardzewiała metalowa szafka pracownicza personelu",
            "Nowoczesny sejf z migającym zamkiem elektronicznym"
        ]
        losowy_opis = random.choice(szafki_opisy)
        proby = self.max_proby

        print(f"\n{C_YELLOW}[ MINI-GRA ] Przed Tobą: {losowy_opis}.")
        print(f"Wpisz cyfrę od 1 do 10. Poziom '{self.diff_txt}' daje Ci {proby} prób!{C_RESET}")

        tajna_liczba = random.randint(1, 10)

        for krok in range(1, proby + 1):
            strz = input(f"Próba {krok}/{proby} >>> ").strip()
            if not strz.isdigit(): 
                print("To nie cyfra... tracisz szansę.")
                continue
            liczba = int(strz)

            if liczba == tajna_liczba:
                print(f"{C_GREEN}[*] KLIK... zapadka puściła! Szafka otwarta.{C_RESET}")
                return True
            elif liczba < tajna_liczba:
                print("Za mało...")
            else:
                print("Za dużo...")

        print(f"{C_RED}[!] Trzask! Wytrych pękł, a głośny hałas rozszedł się po korytarzu!{C_RESET}")
        if random.random() < 0.5: 
            self.straznik_alert(wymuszone=True)
        return False

    def wepchnij_do_eq(self, kategoria, nowy_przedmiot, limit):
        if len(self.plecak[kategoria]) >= limit:
            print(f"\n{C_RED}[!] Brak miejsca w sekcji '{kategoria}' ({limit}/{limit})!{C_RESET}")
            print(f"Znalazłeś: {C_BOLD}{nowy_przedmiot}{C_RESET}")
            wybor = input(f"{C_YELLOW}Wpisz numer itemu do PODMIANY lub 'N' by zostawić: {C_RESET}").strip()

            if wybor.lower() == "n":
                print(f"Zostawiłeś {nowy_przedmiot} na ziemi.")
            else:
                try:
                    idx = int(wybor) - 1
                    if 0 <= idx < len(self.plecak[kategoria]):
                        wyrzucony = self.plecak[kategoria][idx]
                        self.plecak[kategoria][idx] = nowy_przedmiot
                        print(f"{C_GREEN}[*] Wyrzuciłeś {wyrzucony} i schowałeś {nowy_przedmiot}!{C_RESET}")
                except (ValueError, IndexError):
                    print(f"{C_RED}Coś pokręciłeś, przedmiot przepadł bezpowrotnie!{C_RESET}")
        else:
            self.plecak[kategoria].append(nowy_przedmiot)
            print(f"{C_GREEN}[*] Schowałeś {nowy_przedmiot} do plecaka.{C_RESET}")

    def event_handlarz(self):
        print(f"\n{C_BOLD}{C_YELLOW}💰 [!] SPOTKAŁEŚ INNEGO WIĘŹNIA - CZARNY RYNEK! 💰{C_RESET}")

        c_pilnik = max(1, 1 + self.cena_mod)
        c_lina = max(1, 1 + self.cena_mod)
        c_pad = max(1, 2 + self.cena_mod)

        print(f"Modyfikator cen: {self.diff_txt}")
        print(f"1. Kup Pilniczek (Koszt: {c_pilnik} Pączek/ki)")
        print(f"2. Kup Linę (Koszt: {c_lina} Pączek/ki)")
        print(f"3. Kup Spadochron (Koszt: {c_pad} Pączek/ki)")
        print("4. Wyjdź z menu wymiany")

        ile_paczka = self.plecak["Jedzenie"].count("Pączek")
        wybor = input(f"Stan pączków: {ile_paczka}. Twój ruch >>> ").strip()

        if wybor == "1" and ile_paczka >= c_pilnik:
            for _ in range(c_pilnik): self.plecak["Jedzenie"].remove("Pączek")
            self.wepchnij_do_eq("Ucieczka", "Pilniczek", limit=5)
        elif wybor == "2" and ile_paczka >= c_lina:
            for _ in range(c_lina): self.plecak["Jedzenie"].remove("Pączek")
            self.wepchnij_do_eq("Ucieczka", "Lina", limit=5)
        elif wybor == "3" and ile_paczka >= c_pad:
            for _ in range(c_pad): self.plecak["Jedzenie"].remove("Pączek")
            self.wepchnij_do_eq("Ucieczka", "Spadochron", limit=5)
        elif wybor in ["1", "2", "3"]:
            print(f"{C_RED}Brak waluty! Cinkciarz nie daje kredytów.{C_RESET}")
        else:
            print("Więzień znika cicho za rogiem korytarza.")

    def przeszukaj_szafke(self):
        if not self.miniGraZamek(): 
            return

        kat_los = random.randint(1, 3)
        if kat_los == 1:
            znalezisko = random.choice(["Suchy Chleb", "Ciastko", "Jabłko", "Suchy Makaron", "Pączek"])
            x = input(f"{C_YELLOW}Znalazłeś {znalezisko}! Brać? (T/N): {C_RESET}")
            if x.lower() == "t": 
                self.wepchnij_do_eq("Jedzenie", znalezisko, limit=10)
        elif kat_los == 2:
            znalezisko = random.choice(["Pilniczek", "Lina", "Spadochron"])
            x = input(f"{C_YELLOW}Leży tu {znalezisko}! Podnieść szpej? (T/N): {C_RESET}")
            if x.lower() == "t": 
                self.wepchnij_do_eq("Ucieczka", znalezisko, limit=5)
        else:
            x = input(f"{C_YELLOW}Zwykły Kijek. Przyda się jako broń? (T/N): {C_RESET}")
            if x.lower() == "t": 
                self.wepchnij_do_eq("Inne", "Kijek", limit=3)

    def straznik_alert(self, wymuszone=False):
        print(f"\n{C_BOLD}{C_RED}🚨 [!] STRAŻNIK BLISKO! KROKI NA KORYTARZU! 🚨{C_RESET}")

        ma_paczka = "Pączek" in self.plecak["Jedzenie"]
        ma_kijek = "Kijek" in self.plecak["Inne"]

        szansa_ucieczki = (10 if self.stamina >= 50 else 2) + self.bonus_szans
        szansa_kijka = (33 if self.stamina >= 50 else 10) + self.bonus_szans
        
        # dolne limity szans ucieczki
        if szansa_ucieczki < 1: szansa_ucieczki = 1
        if szansa_kijka < 1: szansa_kijka = 1

        print(f"{C_BLUE}Twoja stamina: {self.stamina}%. Co robisz?:{C_RESET}")

        if ma_paczka: print(" 1. Przekup go słodkim pączkiem (100% szans)")
        if ma_kijek: print(f" 2. Atakuj z zaskoczenia kijem ({szansa_kijka}% szans)")
        print(f" 3. Spróbuj uciec w cienie korytarza ({szansa_ucieczki}% szans)")

        wybor = input(f"{C_BOLD}Twój wybór akcji >>> {C_RESET}").strip()

        if wybor == "1" and ma_paczka:
            self.plecak["Jedzenie"].remove("Pączek")
            print(f"{C_GREEN}[*] Strażnik wziął łapówkę i zajął się jedzeniem.{C_RESET}")
        elif wybor == "2" and ma_kijek:
            if random.randint(1, 100) <= szansa_kijka:
                print(f"{C_GREEN}[*] Trafienie! Strażnik osunął się na ziemię.{C_RESET}")
                self.stamina = max(0, self.stamina - 20)
            else:
                self.wpadka()
        else:
            if random.randint(1, 100) <= szansa_ucieczki:
                print(f"{C_GREEN}[*] Szybki bieg uratował Ci skórę. Zgubiłeś pościg.{C_RESET}")
                self.stamina = max(0, self.stamina - 30)
            else:
                self.wpadka()

    def wpadka(self):
        print(f"{C_RED}\n[!] ZŁAPANY! Strażnicy powalili Cię na ziemię!{C_RESET}")
        print(f"{C_RED}Zarekwirowano narzędzia ucieczki oraz przedmioty walki!{C_RESET}")
        self.plecak["Ucieczka"].clear()
        self.plecak["Inne"].clear()
        self.stamina = 40

        print(f"{C_YELLOW}Odsiadujesz swoje... wracasz przymusowo do celi.{C_RESET}")
        self.w_celi = True

        sx = self.c_xmin + (self.c_xmax - self.c_xmin) / 2
        sy = self.c_ymin + (self.c_ymax - self.c_ymin) / 2
        self.t.goto(sx, sy)
        self.t.setheading(90)
        self.X, self.Y = self.t.xcor(), self.t.ycor()


# --- START GRY ---
player = Wiezien()
player.wybierz_poziom()

print(f"\n{C_BOLD}{C_BLUE}=== KONFIGURACJA WIĘZIENIA GENERALNEGO ==={C_RESET}")

# pobranie parametrów od użytkownika w tradycyjnych pętlach
while True:
    szer_muru = input(f"{C_YELLOW}Podaj szerokość murów zewnętrznych: {C_RESET}").strip()
    if szer_muru.isdigit(): 
        break
    print(f"{C_RED}Błąd! Musisz podać cyfry!{C_RESET}")

while True:
    wys_muru = input(f"{C_YELLOW}Podaj wysokość murów zewnętrznych: {C_RESET}").strip()
    if wys_muru.isdigit(): 
        break
    print(f"{C_RED}Błąd! Musisz podać cyfry!{C_RESET}")

player.generuj_mape(int(szer_muru), int(wys_muru))

print(f"{C_GREEN}**Trafiłeś do więzienia, które dawno temu znajdowało się w Niemczech. Jesteś Polakiem i bardzo ciężko jest ci się komunikować, lecz umiesz rozmawiać po angielsku! Wykorzystaj tą umiejętność, aby uciec z więzienia! {C_BOLD}Powodzenia!**{C_RESET}")

# Główna pętla gry pozbawiona sztucznego mapowania funkcji helperami
while gd:
    decyzja = player.menu_wyboru()
    if not gd: 
        break

    if decyzja == 1:
        dist = input(f"{C_YELLOW}Podaj odległość kroku (1-10): {C_RESET}").strip()
        ang = input(f"{C_YELLOW}Podaj kierunek / kąt zwrotu: {C_RESET}").strip()
        player.przemieszczenie(dist, ang)
        player.printStatus()

        wynik_zd = player.akcje_log["Akcje"][-1]
        if wynik_zd == "Pusto":
            continue
        elif wynik_zd == "Policjant zauważył cię":
            player.straznik_alert()
        elif wynik_zd == "Znalazłeś szafkę z rzeczami":
            player.przeszukaj_szafke()
        elif wynik_zd == "Spotkałeś Handlarza":
            player.event_handlarz()

    elif decyzja == 2:
        item = player.zarzadzaj_eq()
        if item and (item in player.plecak["Jedzenie"]):
            player.skonsumuj(item)
        player.printStatus()

    if player.hp_brzuch <= 0:
        print(f"\n{C_RED}{C_BOLD}[!] Głód spadł do zera. Mdlejesz z wycieńczenia... Koniec gry!{C_RESET}")
        player.loguj_wynik("PORAZKA (SMIERC GLODOWA)")
        gd = False

print(f"\n{C_CYAN}Koniec rozgrywki! Kliknij myszką na planszę Turtle, aby zamknąć program.{C_RESET}")
player.wn.exitonclick()