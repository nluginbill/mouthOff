from showCropped import showCropped
from findMouth import retrieveListOfActorFaces


play = True

while play:
	celeb = showCropped(retrieveListOfActorFaces())

	answer = input("Can you guess the celeb?")

	if answer.lower() == celeb["name"].lower():
		print(f"Correct! It's {celeb['name']}")
	else:
		print(f"Ahh, shucks, no, it's {celeb['name']}")

	playAgain = input("Play again? (y/n)")

	if playAgain.lower() != "y":
		play = False