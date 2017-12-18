import static java.awt.BorderLayout.CENTER;
import static java.awt.BorderLayout.NORTH;
import static java.awt.BorderLayout.SOUTH;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Random;
import java.util.Scanner;

import javax.imageio.ImageIO;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.filechooser.FileNameExtensionFilter;

/**
 * The main program for the AdventureGame. Prompts the
 * user for information and leads them through the game, and 
 * also initializes the game setup by requesting a configuration file.
 * @author Shannon Kirby & Doug McNally
 */
public class AdventureGame extends JFrame {
	private static File configFile, roomsFile, itemsFile, imageFile, loadFile;
	private static ArrayList<Room> rooms = new ArrayList<Room>();
	private static ArrayList<Item> items = new ArrayList<Item>();
	private static Adventurer adventurer = new Adventurer();
	private static int totalScore = 0;
	private static JTextArea txtaDesc;
	private static JLabel lblScore;
	private static RandomEvent rndEvent;

	/**
	 * Creates a new AdventureGame Graphical User Interface
	 * that wraps the game and allows for easy and visual
	 * control of the game.
	 */
	public AdventureGame() {
		super("Adventure Game GUI");
		JPanel pnlMain = new JPanel(new BorderLayout());
		JPanel pnlTop = new JPanel(new GridLayout(0, 2, 30, 0));
		JScrollPane pnlMiddle = new JScrollPane();
		JPanel pnlBottom = new JPanel(new FlowLayout());
		JPanel pnlDir = new JPanel(new GridBagLayout());

		JMenuBar menu = new JMenuBar();
		JMenu fileMenu = new JMenu("File");
		JMenu helpMenu = new JMenu("Help");
		JMenuItem fileOpen = new JMenuItem("Open");
		final JMenuItem fileSave = new JMenuItem("Save");
		fileSave.setEnabled(false);
		fileOpen.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JFileChooser fc = new JFileChooser();
				fc.setFileFilter(new FileNameExtensionFilter("Adventure Game File (*.agf)", "agf"));
				int choice = fc.showOpenDialog(AdventureGame.this);
				File targetFile = fc.getSelectedFile();
				if (choice != JFileChooser.APPROVE_OPTION)
					return; // When the user hits cancel on the prompt
				try {
					ObjectInputStream ois = new ObjectInputStream(new FileInputStream(targetFile));
					adventurer = (Adventurer) ois.readObject();
					rooms = (ArrayList<Room>) ois.readObject();
					items = (ArrayList<Item>) ois.readObject();
					try {
						rndEvent = (RandomEvent) ois.readObject();
					} catch (Exception ex) {
						// This was not available in the current game configuration.
						// No problem, just keep going!
					}
					moveAdventurer(adventurer.getRoomPosition(), AdventureGame.this);
					loadFile = targetFile;
					fileSave.setEnabled(true);
					totalScore = 0;
					for(int i = 0; i < items.size(); i ++) {
						if(items.get(i).getPointsGained() > 0)
							totalScore += items.get(i).getPointsGained() * 2;
					}
					for(int i = 0; i < rooms.size(); i++)
						totalScore += rooms.get(i).getPointsGained();
					lblScore.setText("Score = " + adventurer.getScore() + "/" + totalScore);
					JOptionPane.showMessageDialog(AdventureGame.this, "Game loaded successfully.", 
							"Success", JOptionPane.PLAIN_MESSAGE);
				} 
				catch (Exception ex) {
					JOptionPane.showMessageDialog(AdventureGame.this, "That file cannot be opened, please try again.", 
							"Error", JOptionPane.ERROR_MESSAGE);
					return;
				}
			}			
		});
		fileSave.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				try {
					if (JOptionPane.showConfirmDialog(AdventureGame.this, "Are you sure you want to overwrite the existing file?", 
							"Save", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE) == JOptionPane.YES_OPTION) {
						ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(loadFile));
						oos.writeObject(adventurer);
						oos.writeObject(rooms);
						oos.writeObject(items);
						if (rndEvent != null) { oos.writeObject(rndEvent); }
						oos.close();
					} else { return; }
				} catch (Exception ex) {
					JOptionPane.showMessageDialog(AdventureGame.this, "Error saving file. System now exiting.", 
							"Error", JOptionPane.ERROR_MESSAGE);
					System.exit(1);
				}			
			}			
		});
		JMenuItem fileSaveAs = new JMenuItem("Save As...");
		fileSaveAs.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JFileChooser fc = new JFileChooser();
				fc.setFileFilter(new FileNameExtensionFilter("Adventure Game File (*.agf)", "agf"));
				int choice = fc.showSaveDialog(AdventureGame.this);
				File targetFile = fc.getSelectedFile();
				if (choice != JFileChooser.APPROVE_OPTION)
					return; // When the user hits cancel on the prompt
				String ext = targetFile.toString();
				ext = ext.substring(ext.length()-4, ext.length());
				targetFile = ext.equals(".agf") ? targetFile : new File(targetFile.toString() + ".agf");
				try {
					ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(targetFile));
					oos.writeObject(adventurer);
					oos.writeObject(rooms);
					oos.writeObject(items);
					if (rndEvent != null) { oos.writeObject(rndEvent); }
					oos.close();
				} catch (Exception ex) {
					JOptionPane.showMessageDialog(AdventureGame.this, "Error saving file. System now exiting.", 
							"Error", JOptionPane.ERROR_MESSAGE);
					System.exit(1);
				}			
			}			
		});
		JMenuItem fileExit = new JMenuItem("Exit");
		fileExit.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				System.exit(0);		
			}			
		});
		JMenuItem helpAbout = new JMenuItem("About");
		helpAbout.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JOptionPane.showMessageDialog(AdventureGame.this, "For assistance please read the included readme.txt file.\n" +
						"AdventureGame Made by Shannon Kirby and Doug McNally for CSE 271, Miami University", 
						"Help", JOptionPane.INFORMATION_MESSAGE);		
			}			
		});

		fileMenu.add(fileOpen);
		fileMenu.add(fileSave);
		fileMenu.add(fileSaveAs);
		fileMenu.addSeparator();
		fileMenu.add(fileExit);

		helpMenu.add(helpAbout);

		menu.add(fileMenu);
		menu.add(helpMenu);

		setJMenuBar(menu);

		JButton btnN = new JButton("N");
		btnN.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JOptionPane.showMessageDialog(AdventureGame.this, 
						rooms.get(adventurer.getRoomPosition() - 1).getNorthDescription(), "North",
						JOptionPane.INFORMATION_MESSAGE);
				moveAdventurer(rooms.get(adventurer.getRoomPosition() - 1).getNorthNumber(), AdventureGame.this);	
			}
		});
		JButton btnS = new JButton("S");
		btnS.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JOptionPane.showMessageDialog(AdventureGame.this, 
						rooms.get(adventurer.getRoomPosition() - 1).getSouthDescription(), "South",
						JOptionPane.INFORMATION_MESSAGE);
				moveAdventurer(rooms.get(adventurer.getRoomPosition() - 1).getSouthNumber(), AdventureGame.this);			
			}			
		});
		JButton btnW = new JButton("W");
		btnW.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JOptionPane.showMessageDialog(AdventureGame.this, 
						rooms.get(adventurer.getRoomPosition() - 1).getWestDescription(), "West",
						JOptionPane.INFORMATION_MESSAGE);
				moveAdventurer(rooms.get(adventurer.getRoomPosition() - 1).getWestNumber(), AdventureGame.this);			
			}			
		});
		JButton btnE = new JButton("E");
		btnE.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JOptionPane.showMessageDialog(AdventureGame.this, 
						rooms.get(adventurer.getRoomPosition() - 1).getEastDescription(), "East",
						JOptionPane.INFORMATION_MESSAGE);
				moveAdventurer(rooms.get(adventurer.getRoomPosition() - 1).getEastNumber(), AdventureGame.this);			
			}			
		});
		JButton btnInv = new JButton("Inventory");
		btnInv.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				String inven;
				if (adventurer.getInventory().size() > 0) {
					inven = "You have the following items:\n";
					for(int i = 0; i < adventurer.getInventory().size(); i++) 
						inven += adventurer.getInventory().get(i).getName() + "\n";	
				} else
					inven = "Your inventory is currently empty.";
				JOptionPane.showMessageDialog(AdventureGame.this, inven, "Inventory", JOptionPane.INFORMATION_MESSAGE);
			}			
		});
		final JTextField txtCmd = new JTextField(30);
		JButton btnSubmit = new JButton("Submit");
		btnSubmit.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				AdventureGame.handleUserInput(txtCmd.getText(), AdventureGame.this);
				txtCmd.setText(null);
			}			
		});
		txtaDesc = new JTextArea();
		JLabel lblCmd = new JLabel("Command: ");
		lblScore = new JLabel();

		GridBagConstraints c = new GridBagConstraints();
		c.insets = new Insets(5, 5, 5, 5);
		c.gridx = 1;
		c.gridy = 0;
		pnlDir.add(btnN, c);
		c.gridy = 2;
		pnlDir.add(btnS, c);
		c.gridx = 0;
		c.gridy = 1;
		pnlDir.add(btnW, c);
		c.gridx = 2;
		pnlDir.add(btnE, c);
		c.gridy = 3;
		c.gridx = 0;
		c.gridwidth = 3;
		pnlDir.add(btnInv, c);
		c.gridy = 4;
		pnlDir.add(lblScore, c);

		Image mapImage = null;
		JLabel lblImage = new JLabel();
		if (imageFile != null) {
			try {
				mapImage = ImageIO.read(imageFile);
				lblImage.setIcon(new ImageIcon(mapImage));
			} catch (IOException e) {
				JOptionPane.showMessageDialog(this, "Failed to load the map image.", 
						"Error", JOptionPane.ERROR_MESSAGE);
			}
		}
		if (mapImage == null) {
			lblImage.setText("No Map Loaded.");
		}

		JPanel pnlImage = new JPanel(new FlowLayout());
		pnlImage.add(lblImage);
		pnlTop.add(pnlImage);
		pnlTop.add(pnlDir);

		pnlMiddle.setBorder(BorderFactory.createTitledBorder("Current Location: "));
		pnlMiddle.setPreferredSize(new Dimension(0, 150));
		pnlMiddle.setViewportView(txtaDesc);
		txtaDesc.setLineWrap(true);
		txtaDesc.setWrapStyleWord(true);
		txtaDesc.setEditable(false);
		txtaDesc.setOpaque(false);

		pnlBottom.add(lblCmd);
		pnlBottom.add(txtCmd);
		pnlBottom.add(btnSubmit);

		this.getRootPane().setDefaultButton(btnSubmit);

		pnlMain.add(pnlTop, NORTH);
		pnlMain.add(pnlMiddle, CENTER);
		pnlMain.add(pnlBottom, SOUTH);
		this.add(pnlMain);
	}

	public static void main(String[] args) {
		String choice = JOptionPane.showInputDialog(null, "Enter configuration file name: ", 
				"AdventureGame Config", JOptionPane.QUESTION_MESSAGE);
		try {
			configFile = new File(choice);
			findFiles(configFile);
		} catch (Exception e) {
			System.out.println("That was not a valid configuration file.  System exiting.");
			System.exit(1);
		}
		initializeRooms(roomsFile);
		initializeItems(itemsFile);
		AdventureGame gui = new AdventureGame();
		gui.setResizable(false);
		gui.setDefaultCloseOperation(EXIT_ON_CLOSE);
		gui.pack();
		gui.setLocationRelativeTo(null);		
		gui.setVisible(true);

		adventurer = new Adventurer();
		for(int i = 0; i < items.size(); i ++) {
			if(items.get(i).getPointsGained() > 0)
				totalScore += items.get(i).getPointsGained() * 2;
		}
		for(int i = 0; i < rooms.size(); i++)
			totalScore += rooms.get(i).getPointsGained();
		moveAdventurer(adventurer.getRoomPosition(), gui);
	}

	/**
	 * The main control for this program that takes user
	 * input and then responds to it appropriately if it
	 * is a recognized command.
	 * @param input the command requested to be executed 
	 */
	protected static void handleUserInput(String input, AdventureGame parent) {
		input = input.toLowerCase();
		if (input.equalsIgnoreCase("score")) {
			String score = "Current score = " + adventurer.getScore() + " out of " + totalScore;
			JOptionPane.showMessageDialog(parent, score, "Current Score", JOptionPane.INFORMATION_MESSAGE);
		}
		else if (input.equalsIgnoreCase("exit") || input.equalsIgnoreCase("quit")) {
			String score = "Thank you for plaing.\n  Your score = " + adventurer.getScore() + 
			" out of " + totalScore;
			JOptionPane.showMessageDialog(parent, score, "Current Score", JOptionPane.PLAIN_MESSAGE);
			System.exit(0);
		}
		else if (input.startsWith("take") || input.startsWith("get") ||
				input.startsWith("grab") || input.startsWith("pick up")) {
			boolean itemHere = false;
			for(int i = 0; i < items.size(); i++) {
				if(items.get(i).getCurrentPosition() == adventurer.getRoomPosition() && 
						input.endsWith(items.get(i).getName().toLowerCase())) {
					JOptionPane.showMessageDialog(parent, items.get(i).getPickupDescription(), 
							"Item Obtained", JOptionPane.INFORMATION_MESSAGE);
					adventurer.addItem(items.get(i));
					lblScore.setText("Score = " + adventurer.getScore() + "/" + totalScore);
					itemHere = true;
				}
			}
			if (!itemHere) { 
				String[] strSplit = input.split(" ");
				String message = "I see no " + strSplit[strSplit.length - 1] + " here."; // Fix what we did before for multi-word items
				JOptionPane.showMessageDialog(parent, message, "Whoops", JOptionPane.WARNING_MESSAGE);
			}
		}
		else if (input.startsWith("put") || input.startsWith("drop")) {
			if(input.endsWith("all")) {
				for (int i = 0; i < items.size(); i++) {
					if (items.get(i).getCurrentPosition() == -1) {
						adventurer.dropItem(items.get(i));
						lblScore.setText("Score = " + adventurer.getScore() + "/" + totalScore);
					}
				}
				JOptionPane.showMessageDialog(parent, "All of your items have been placed on the ground", 
						"Items Dropped", JOptionPane.INFORMATION_MESSAGE);
			}
			else {
				

				boolean itemHere = false;
				for (int i = 0; i < items.size(); i++) {
					if (items.get(i).getCurrentPosition() == -1 && 
							input.endsWith(items.get(i).getName().toLowerCase())) {
						JOptionPane.showMessageDialog(parent, items.get(i).getDropDescription(), 
								"Item Dropped", JOptionPane.INFORMATION_MESSAGE);
						adventurer.dropItem(items.get(i));
						lblScore.setText("Score = " + adventurer.getScore() + "/" + totalScore);
						itemHere = true;
					}
				}
				if (!itemHere) { 
					String message = "You don't have one of those to " + input.split(" ")[0] + "."; // Fix what we did before for multi-word items
					JOptionPane.showMessageDialog(parent, message, "Whoops", JOptionPane.WARNING_MESSAGE);
				}
			}
		}
		else if (input.equals("raptor")) { // Magic word
			JOptionPane.showMessageDialog(parent, "A raptor appears moving at 20m/s toward you.  You have 5 seconds to live.  Make your time.");
			try{
				Thread.currentThread();
				Thread.sleep(5000);
			}
			catch(Exception e){
			} finally {
				adventurer.addPoints(-adventurer.getScore());
				lblScore.setText("Score = EPIC FAIL");
				JOptionPane.showMessageDialog(parent, "The raptor has killed you and stolen all of your belongings.", 
						"Dead.", JOptionPane.WARNING_MESSAGE);
				parent.removeAll();
			}
		}
		else if(input.equals("triceratops")) {
			moveAdventurer(rooms.size() - 1, parent);
			JOptionPane.showMessageDialog(parent, "A mystical triceratops tells you to hop on his back for a wonderous" +
					" ride.", "Triceratops", JOptionPane.WARNING_MESSAGE);
		}
		else if(input.startsWith("pterodactyl")) {
			int choice;
			try {
				choice = Integer.parseInt(input.split(" ")[1]);
			}
			catch (NumberFormatException ex) {
				return;
			}
			if(choice > 0 && choice < rooms.size()) {
				moveAdventurer(choice, parent);
				JOptionPane.showMessageDialog(parent, "A glorious pterodactyl grabs you with his majestic talons and " +
						"carries you to room " + choice + "!", "Pterodactyl", JOptionPane.WARNING_MESSAGE);
			}
		}
		else {
			JOptionPane.showMessageDialog(parent, "What did you say!?!?", "Error.", JOptionPane.WARNING_MESSAGE);
		}
	}

	/**
	 * Finds the files listed in the 
	 * Configuration file for the game.
	 * @param file The location of the Configuration file.
	 */
	public static void findFiles(File file) throws IOException {
		FileInputStream fis = new FileInputStream(file);
		Scanner sc = new Scanner(fis);
		roomsFile = new File(sc.nextLine());
		itemsFile = new File(sc.nextLine());
		if (sc.hasNext())
			imageFile = new File(sc.nextLine());
		sc.close();
	}

	/**
	 * Setup the rooms in this game given a file
	 * containing the information about the rooms.
	 * @param roomsFile File that contains room information
	 */
	public static void initializeRooms(File roomsFile) {
		try {
			FileInputStream fis = new FileInputStream(roomsFile);
			Scanner sc = new Scanner(fis);
			String roomDescription = "";
			String line, northDescription, southDescription, eastDescription, westDescription;
			int roomNumber, pointsGained, northNumber, southNumber, eastNumber, westNumber;
			int i = 0;

			while(sc.hasNext()) {
				roomNumber = 1;
				sc.nextLine();
				while(true) {
					line = sc.nextLine();
					if(line.compareTo("END") == 0) {
						break;
					}
					roomDescription += line + "\n";
				}
				pointsGained = sc.nextInt();
				sc.nextLine();
				northNumber = sc.nextInt();
				northDescription = sc.nextLine();
				southNumber = sc.nextInt();
				southDescription = sc.nextLine();
				eastNumber = sc.nextInt();
				eastDescription = sc.nextLine();
				westNumber = sc.nextInt();
				westDescription = sc.nextLine();
				rooms.add(new Room(roomNumber, roomDescription, pointsGained, northNumber, northDescription,
						southNumber, southDescription, eastNumber, eastDescription, westNumber, westDescription));
				roomDescription = "";
				i++;
			}
			sc.close();
		} catch (FileNotFoundException e) {
			System.out.println("Error reading the rooms file.  System exiting.");
			System.exit(1);
		}
	}

	/**
	 * Create all of the items in this AdventureGame and
	 * place them initially in the proper places given
	 * a file that has information about them.
	 * @param itemsFile The file containing information about the items.
	 */
	public static void initializeItems(File itemsFile) {
		try {
			FileInputStream fis = new FileInputStream(itemsFile);
			Scanner sc = new Scanner(fis);
			String name, roomDescription, pickupDescription, dropDescription;
			int initialNumber, pointsGained;

			while(sc.hasNext()) {
				name = sc.nextLine();
				if (!name.equals("RANDOM")){  
					roomDescription = sc.nextLine();
					pickupDescription = sc.nextLine();
					dropDescription = sc.nextLine();
					initialNumber = sc.nextInt();
					sc.nextLine();
					pointsGained = sc.nextInt();
					if(sc.hasNext()) {
						sc.nextLine();
					}
					items.add(new Item(name, roomDescription, pickupDescription, dropDescription,
							initialNumber, pointsGained));
				} else {
					name = sc.nextLine();
					String actionDescription = sc.nextLine();
					String itemTmp = sc.nextLine();
					Item item = null;
					for (int i = 0; i < items.size(); i++) {
						if (items.get(i).getName().equals(itemTmp)) {
							item = items.get(i);
							break;
						}
					}
					float prb = Float.parseFloat(sc.nextLine());
					rndEvent = new RandomEvent(name, actionDescription, prb, item);
				}
			}
			sc.close();
		} catch (FileNotFoundException e) {
			System.out.println("Error reading the items file.  System exiting.");
			System.exit(1);
		}
	}

	/**
	 * Checks if the Adventurer has entered the room at roomPosition
	 * before, and if not awards the appropriate number of points.
	 * @param roomPosition the room being entered
	 */
	public static void enteredRoomTest(int roomPosition, AdventureGame gui) {
		if(!rooms.get(roomPosition - 1).getHasEntered() && roomPosition - 1 != 0) {
			adventurer.addPoints(rooms.get(roomPosition - 1).getPointsGained());
			rooms.get(roomPosition - 1).setHasEnteredTrue();
		}
		for(int i = 0; i < items.size(); i++) {
			if(items.get(i).getCurrentPosition() == roomPosition) {
				txtaDesc.setText(txtaDesc.getText() + items.get(i).getDropDescription() + "\n");
			}
		}
		if (rndEvent != null)
			if (rndEvent.getItem().getCurrentPosition() == -1 
					&& new Random().nextFloat() < rndEvent.getProbability()) {
				lblScore.setText("YOU LOSE!");
				JOptionPane.showMessageDialog(gui, rndEvent.getActionDescription(), 
						rndEvent.getName(), JOptionPane.ERROR_MESSAGE);
				gui.removeAll();
			}
	}

	/**
	 * Moves the adventurer to a new room.
	 * @param newRoomPosition the room to which to move the adventurer
	 */
	public static void moveAdventurer(int newRoomPosition, AdventureGame gui) {
		if(newRoomPosition != -1) {
			adventurer.setRoomPosition(newRoomPosition);
		}
		txtaDesc.setText("Current Room # " + (adventurer.getRoomPosition()) + "\n" + 
				rooms.get(adventurer.getRoomPosition() - 1).getRoomDescription() + "\n");
		enteredRoomTest(adventurer.getRoomPosition(), gui);
		lblScore.setText("Score = " + adventurer.getScore() + "/" + totalScore);
	}
}