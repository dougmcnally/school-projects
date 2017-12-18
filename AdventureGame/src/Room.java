import java.io.Serializable;

/**
 * Models a Room in an adventure game through
 * which Items and Adventurers can move.
 * @author Shannon Kirby and Doug McNally
 */
public class Room implements Serializable {
	private int roomNumber, pointsGained, northNumber, southNumber, eastNumber, westNumber;
	private String roomDescription, northDescription, southDescription, eastDescription, westDescription;
	private boolean hasEntered;

	/**
	 * Creates a new Room given a number representing its position,
	 * a description, how many points it is worth, and the descriptions 
	 * of what is to the north, west, east, and south of this Room.
	 * @param roomNumber
	 * @param roomDescription
	 * @param pointsGained
	 * @param northNumber
	 * @param northDescription
	 * @param southNumber
	 * @param southDescription
	 * @param eastNumber
	 * @param eastDescription
	 * @param westNumber
	 * @param westDescription
	 */
	public Room(int roomNumber, String roomDescription, int pointsGained, int northNumber,
			String northDescription, int southNumber, String southDescription, int eastNumber,
			String eastDescription, int westNumber, String westDescription) {
		this.roomNumber = roomNumber;
		this.roomDescription = roomDescription;
		this.pointsGained = pointsGained;
		this.northNumber = northNumber;
		this.northDescription = northDescription;
		this.southNumber = southNumber;
		this.southDescription = southDescription;
		this.eastNumber = eastNumber;
		this.eastDescription = eastDescription;
		this.westNumber = westNumber;
		this.westDescription = westDescription;
		hasEntered = false;
	}

	public String getEastDescription() {
		return eastDescription;
	}

	public int getEastNumber() {
		return eastNumber;
	}

	public boolean getHasEntered() {
		return hasEntered;
	}

	public String getNorthDescription() {
		return northDescription;
	}

	public int getNorthNumber() {
		return northNumber;
	}

	public int getPointsGained() {
		return pointsGained;
	}

	public String getRoomDescription() {
		return roomDescription;
	}

	public int getRoomNumber() {
		return roomNumber;
	}

	public String getSouthDescription() {
		return southDescription;
	}

	public int getSouthNumber() {
		return southNumber;
	}

	public String getWestDescription() {
		return westDescription;
	}

	public int getWestNumber() {
		return westNumber;
	}

	public void setHasEnteredTrue() {
		hasEntered = true;
	}
}