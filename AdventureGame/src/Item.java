import java.io.Serializable;

/**
 * Models an item in an adventure game.
 * @author Shannon Kirby and Doug McNally
 */
public class Item implements Serializable {
	private String name, roomDescription, pickupDescription, dropDescription;
	private int initialPosition, currentPosition, pointsGained;

	/**
	 * Create an item given a name, description of the room that it is in, 
	 * descriptions of what happens when it is dropped or picked up, its 
	 * starting position and how many points it is worth.
	 * @param name
	 * @param roomDescription
	 * @param pickupDescription
	 * @param dropDescription
	 * @param initialPosition
	 * @param pointsGained
	 */
	public Item(String name, String roomDescription, String pickupDescription, String dropDescription,
			int initialPosition, int pointsGained) {
		this.name = name;
		this.roomDescription = roomDescription;
		this.pickupDescription = pickupDescription;
		this.dropDescription = dropDescription;
		this.initialPosition = initialPosition;
		this.currentPosition = initialPosition;
		this.pointsGained = pointsGained;
	}

	/**
	 * Create a deep copy of the <em>item</em>.
	 * @param item The item to be copied
	 */
	public Item(Item item) {
		name = item.getName();
		roomDescription = item.getRoomDescription();
		pickupDescription = item.getPickupDescription();
		dropDescription = item.getDropDescription();
		initialPosition = item.getInitialPosition();
		currentPosition = item. getCurrentPosition();
		pointsGained = item.getPointsGained();
	}

	public String getName() {
		return name;
	}

	public String getRoomDescription() {
		return roomDescription;
	}

	public String getPickupDescription() {
		return pickupDescription;
	}

	public String getDropDescription() {
		return dropDescription;
	}

	public int getInitialPosition() {
		return initialPosition;
	}

	public int getCurrentPosition() {
		return currentPosition;
	}

	public int getPointsGained() {
		return pointsGained;
	}

	public void setCurrentPosition(int currentPosition) {
		this.currentPosition = currentPosition;
	}

	public void pickUp() {
		currentPosition = -1;
	}
}