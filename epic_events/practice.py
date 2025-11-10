import click

def afficher_menu():
    print("\n--- Menu Principal ---")
    print("1. Arrivée")
    print("2. Départ")
    print("3. Quitter")

def menu_arrivee():
    print("\n--- Sous-menu Arrivée ---")
    print("1. Bonjour!")
    print("2. Comment ça va?")
    print("3. Retour")
    choix = input("Choix : ")
    if choix == "1":
        click.echo("Bonjour!")
    elif choix == "2":
        click.echo("Comment ça va?")
    elif choix == "3":
        return
    else:
        print("Choix invalide")

def menu_depart():
    print("\n--- Sous-menu Départ ---")
    print("1. Au revoir")
    print("2. À bientôt")
    print("3. Retour")
    choix = input("Choix : ")
    if choix == "1":
        click.echo("Au revoir!")
    elif choix == "2":
        click.echo("À bientôt!")
    elif choix == "3":
        return
    else:
        print("Choix invalide")

def main():
    while True:
        afficher_menu()
        choix = input("Choix : ")
        if choix == "1":
            menu_arrivee()
        elif choix == "2":
            menu_depart()
        elif choix == "3":
            print("Au revoir!")
            break
        else:
            print("Choix invalide")

if __name__ == '__main__':
    main()
