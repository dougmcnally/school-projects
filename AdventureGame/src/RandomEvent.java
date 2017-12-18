import java.io.Serializable;

/**
 * Stores a random event for the user to encounter
 * and an item that they must have for it to occur.  
 * Also a probability of encountering this random event
 * is stored and is in (0, 1]
 * @author Shannon Kirby and Doug McNally
 *
 */
public class RandomEvent implements Serializable {
	private String name;
	private float probability;
	private Item item;
	private String actionDescription;
	/**
	 * Creates a RandomEvent with a given name, description, trigger item,
	 * and probability of appearing.
	 * @param name
	 * @param actionDescription
	 * @param probability
	 * @param item
	 */
	public RandomEvent(String name, String actionDescription, float probability, Item item) {
		this.name = name;
		this.actionDescription = actionDescription;
		this.probability = probability;
		this.item = item;
	}
	
	public String getName() {
		return name;
	}
	
	public float getProbability() {
		return probability;
	}
	
	public Item getItem() {
		return item;
	}
	
	public String getActionDescription() {
		return actionDescription;
	}
}
