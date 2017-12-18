import java.io.Serializable;
import java.util.ArrayList;

/**
 * Models an adventurer in a game who has an inventory,
 * score and spatial position.
 * @author Shannon Kirby & Doug McNally
 */
public class Adventurer implements Serializable {
	private ArrayList<Item> inventory;
	private int score;
	private int roomPosition;

	/**
	 * Creates an Adventurer with an empty inventory
	 * zero score, and default starting position.
	 */
	public Adventurer() {
		inventory = new ArrayList<Item>();
		score = 0;
		roomPosition = 1;
	}

	public ArrayList<Item> getInventory() {
		return inventory;
	}

	public int getScore() {
		return score;
	}

	public int getRoomPosition() {
		return roomPosition;
	}

	/**
	 * Adds an item to this Adventurer's inventory.
	 * @param item The Item to add
	 */
	public void addItem(Item item) {
		inventory.add(item);
		item.setCurrentPosition(-1);
		if(item.getPointsGained() > 0) {
			if(roomPosition != 1) {
				score += item.getPointsGained();
			}
			else {
				score -= item.getPointsGained();
			} 
		}
		else {
			if(roomPosition == item.getInitialPosition()) {
				score += item.getPointsGained();
			}
		}
	}

	/**
	 * Removes an item from this Adventurer's inventory.
	 * @param item the Item to drop
	 */
	public void dropItem(Item item) {
		inventory.remove(item);
		item.setCurrentPosition(getRoomPosition());
		if(item.getPointsGained() > 0) {
			if(roomPosition == 1) {
				score += item.getPointsGained();
			}
			else {
				score -= item.getPointsGained();
			}
		}
		else {
			if(roomPosition == item.getInitialPosition()) {
				score -= item.getPointsGained();
			}
		}
	}

	public void addPoints(int points) {
		score += points;
	}

	public void setRoomPosition(int roomPosition) {
		this.roomPosition = roomPosition;
	}
}