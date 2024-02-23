package game;
import javax.swing.*;

import java.awt.*;
import java.awt.event.*;

public class MineSweapPart extends JFrame

{
	private static final long serialVersionUID = 1L;
	private static final int WINDOW_HEIGHT = 760;
	private static final int WINDOW_WIDTH = 760;
	private static final int MINE_GRID_ROWS = 16;
	private static final int MINE_GRID_COLS = 16;
	private static final int TOTAL_MINES = 10;
	private static final int NO_MINES_IN_PERIMETER_GRID_VALUE = 0;
	private static final int ALL_MINES_IN_PERIMETER_GRID_VALUE = 8;
	private static final int IS_A_MINE_IN_GRID_VALUE = 9;

	private static int guessedMinesLeft = TOTAL_MINES;
	private static int actualMinesLeft = TOTAL_MINES;

	private static final String UNEXPOSED_FLAGGED_MINE_SYMBOL = "!";
	private static final String EXPOSED_MINE_SYMBOL = "BOMB";

	// visual indication of an exposed MyJButton
	private static final Color CELL_EXPOSED_BACKGROUND_COLOR = Color.black;
	// colors used when displaying the getStateStr() String
	private static final Color CELL_EXPOSED_FOREGROUND_COLOR_MAP[] = {Color.lightGray, Color.blue, Color.magenta, Color.pink, Color.yellow, 
			Color.orange, Color.magenta, Color.magenta, Color.red, Color.red};

	private boolean running = true;
	// holds the "number of mines in perimeter" value for each MyJButton 
	private int[][] mineGrid = new int[MINE_GRID_ROWS][MINE_GRID_COLS];

	public MineSweapPart()
	{	
		this.setTitle("MineSweap\t\t\t" +  MineSweapPart.guessedMinesLeft +" Mines left");
		this.setSize(WINDOW_WIDTH, WINDOW_HEIGHT);
		this.setResizable(false);
		this.setLayout(new GridLayout(MINE_GRID_ROWS, MINE_GRID_COLS, 0, 0));
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);

		this.createContents();
		// place MINES number of mines in mineGrid and adjust all of the "mines in perimeter" values
		this.setMines();
		this.setVisible(true);

	}
	public void createContents()
	{
		for (int gr = 0; gr < MINE_GRID_ROWS; ++gr)
		{  
			for (int gc = 0; gc < MINE_GRID_COLS; ++gc)
			{  
				// set sGrid[gr][gc] entry to 0 - no mines in it's perimeter
				this.mineGrid[gr][gc] = 0; 
				// create a MyJButton that will be at location (br, bc) in the GridLayout
				MyJButton but = new MyJButton("", gr, gc); 
				// register the event handler with this MyJbutton
				but.addActionListener(new MyListener());
				// add the MyJButton to the GridLayout collection
				this.add(but);
			}  
		}
	}

	// place TOTAL_MINES number of mines in mineGrid and adjust all of the "mines in perimeter" values
	// 40 pts
	private void setMines()
	{
		for(int i=0; i<TOTAL_MINES; i++) {
			int randRow = (int)(Math.random() * MINE_GRID_ROWS);
			int randCol = (int)(Math.random() * MINE_GRID_COLS );
			if(!(mineGrid[randRow][randCol] == IS_A_MINE_IN_GRID_VALUE)){ 
				mineGrid[randRow][randCol] = IS_A_MINE_IN_GRID_VALUE;

				if(randRow + 1 < mineGrid.length){
					if(mineGrid[randRow+1][randCol] != IS_A_MINE_IN_GRID_VALUE){
						mineGrid[randRow+1][randCol]++;
					}
					if(randCol + 1 < mineGrid[randRow+1].length && mineGrid[randRow+1][randCol+1] != IS_A_MINE_IN_GRID_VALUE ){
						mineGrid[randRow+1][randCol+1]++;
					}
					if(randCol-1 >= 0 && mineGrid[randRow+1][randCol-1] != IS_A_MINE_IN_GRID_VALUE){
						mineGrid[randRow+1][randCol-1]++;
					}
				}
				if(randRow - 1 >= 0 ){
					if(mineGrid[randRow-1][randCol] != IS_A_MINE_IN_GRID_VALUE){
						mineGrid[randRow-1][randCol]++;
					}
					if(randCol + 1 < mineGrid[randRow-1].length && mineGrid[randRow-1][randCol+1] != 9){
						mineGrid[randRow-1][randCol+1]++;
					}
					if(randCol- 1 >= 0 && mineGrid[randRow-1][randCol-1] != IS_A_MINE_IN_GRID_VALUE){
						mineGrid[randRow-1][randCol-1]++;
					}
				}
				if(randCol + 1 < mineGrid[randRow].length && mineGrid[randRow][randCol+1] != 9){ 
					mineGrid[randRow][randCol+1]++; 
				}
				if(randCol- 1 >= 0 && mineGrid[randRow][randCol-1] != IS_A_MINE_IN_GRID_VALUE )
				{ 
					mineGrid[randRow][randCol-1]++;
				}
			}
//			} else{
//				i--; 
//			}
		}
	}
	// your code here ...


	private String getGridValueStr(int row, int col)
	{
		// no mines in this MyJbutton's perimeter
		if ( this.mineGrid[row][col] == NO_MINES_IN_PERIMETER_GRID_VALUE )
			return "0";
		// 1 to 8 mines in this MyJButton's perimeter
		else if ( this.mineGrid[row][col] > NO_MINES_IN_PERIMETER_GRID_VALUE && 
				this.mineGrid[row][col] <= ALL_MINES_IN_PERIMETER_GRID_VALUE )
			return "" + this.mineGrid[row][col];
		// this MyJButton in a mine
		else // this.mineGrid[row][col] = IS_A_MINE_IN_GRID_VALUE
			return MineSweapPart.EXPOSED_MINE_SYMBOL;
	}
	// nested private class
	private class MyListener implements ActionListener
	{
		public void actionPerformed(ActionEvent event)
		{
			// used to determine if ctrl or alt key was pressed at the time of mouse action
			if(running) 
			{
				int mod = event.getModifiers();
				MyJButton mjb = (MyJButton)event.getSource();
				// is the MyJbutton that the mouse action occurred in flagged

				boolean flagged = mjb.getText().equals(MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL);
				// is the MyJbutton that the mouse action occurred in already exposed
				boolean exposed = mjb.getBackground().equals(CELL_EXPOSED_BACKGROUND_COLOR);
				// flag a cell : ctrl + left click


				if ( !flagged && !exposed && (mod & ActionEvent.CTRL_MASK) != 0 )
				{
//				if(!MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL.equalsIgnoreCase(EXPOSED_MINE_SYMBOL)) {
//						mjb.setText(UNEXPOSED_FLAGGED_MINE_SYMBOL);
//						mjb.setForeground(Color.red);
//					}
//					else {
//						mjb.setText(UNEXPOSED_FLAGGED_MINE_SYMBOL);
//						mjb.setForeground(Color.green);
//					}
//					System.out.print(MineSweapPart.guessedMinesLeft + " ");
					if(MineSweapPart.guessedMinesLeft==0) {
						return;
					}
					mjb.setText(MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL);
					--MineSweapPart.guessedMinesLeft;
					// if the MyJbutton that the mouse action occurred in is a mine
					// 10 pts
					if ( mineGrid[mjb.ROW][mjb.COL] == IS_A_MINE_IN_GRID_VALUE )
					{
						MineSweapPart.actualMinesLeft-- ;
//						MineSweapPart.guessedMinesLeft--;
						if( actualMinesLeft==0) {
							JOptionPane.showMessageDialog(null, " You Win ");
							running = false;
//							return;
						}	
					}
					setTitle("MineSweap - " + MineSweapPart.guessedMinesLeft +" Mines left");
//					System.out.println(MineSweapPart.guessedMinesLeft);
				}
				// unflag a cell : alt + left click
				else if ( flagged && !exposed && (mod & ActionEvent.SHIFT_MASK) != 0 )
				{
					mjb.setText("");
					if(mineGrid[mjb.ROW][mjb.COL]==IS_A_MINE_IN_GRID_VALUE) {
						++MineSweapPart.actualMinesLeft;
					}
					// if the MyJbutton that the mouse action occurred in is a mine
					// 10 pts
					++MineSweapPart.guessedMinesLeft;
//					if ( mineGrid[mjb.ROW][mjb.COL] == IS_A_MINE_IN_GRID_VALUE )
//					{
//						
//						// what else do you need to adjust?
//						// could the game be over?
//					}
					setTitle("MineSweap - " + 
							MineSweapPart.guessedMinesLeft +" Mines left");
				}
				// expose a cell : left click
				else if ( !flagged && !exposed )
				{
					if (mineGrid[mjb.ROW][mjb.COL] == IS_A_MINE_IN_GRID_VALUE)
						for (int x = 0; x < mineGrid.length; x++) {
							for (int y = 0; y < mineGrid[x].length; y++) {
								int index = ((mjb.ROW+x)*MineSweapPart.MINE_GRID_ROWS) + mjb.COL+y;
								MyJButton newButton = (MyJButton)(mjb.getParent().getComponent(index));
								if (newButton.getText().equals(UNEXPOSED_FLAGGED_MINE_SYMBOL)) {
									newButton.setForeground(Color.red);
								}
							}
						}
					exposeCell(mjb);
				}  
			}
		}

	}

	public void exposeCell(MyJButton mjb)
	{
		if ( !running )
			return;

		// expose this MyJButton 
		mjb.setBackground(CELL_EXPOSED_BACKGROUND_COLOR);
		mjb.setForeground(CELL_EXPOSED_FOREGROUND_COLOR_MAP[mineGrid[mjb.ROW][mjb.COL]]);
		mjb.setText(getGridValueStr(mjb.ROW, mjb.COL));

		// if the MyJButton that was just exposed is a mine
		// 20 pts

		if ( mineGrid[mjb.ROW][mjb.COL] == IS_A_MINE_IN_GRID_VALUE )
		{  
			for(int x = -MINE_GRID_ROWS; x<MINE_GRID_ROWS; x++){
				
				for(int y = -MINE_GRID_COLS; y<MINE_GRID_COLS; y++){
//					if (mineGrid[x][y] == IS_A_MINE_IN_GRID_VALUE) {
//						int index = x + y
//						exposeCell()
//					}

//					System.out.println(mjb.ROW + ":" + mjb.COL + ":" + x + ":" + y);
					if(mjb.getText().equals(MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL) /*&& mineGrid[mjb.ROW][mjb.COL] != IS_A_MINE_IN_GRID_VALUE*/) {
						
//						mjb.setText(UNEXPOSED_FLAGGED_MINE_SYMBOL);
						System.out.println(mjb.ROW + ":" + mjb.COL + ":" + x + ":" + y);
//						mjb.setForeground(Color.RED);
					}
					
					if(!(x == 0 && y == 0) &&(mjb.ROW+x >= 0) && (mjb.ROW+x <MineSweapPart.MINE_GRID_ROWS) && (mjb.COL+y >= 0) && (mjb.COL+y < MineSweapPart.MINE_GRID_COLS)){
						int index = ((mjb.ROW+x)*MineSweapPart.MINE_GRID_ROWS) + mjb.COL+y;

						
//						if(!MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL.equalsIgnoreCase(EXPOSED_MINE_SYMBOL)) {
//							mjb.setText(UNEXPOSED_FLAGGED_MINE_SYMBOL);
//							mjb.setForeground(Color.red);
//						}
						MyJButton newButton = (MyJButton)(mjb.getParent().getComponent(index));
						if (!newButton.getText().equals(MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL)&&!newButton.getBackground().equals(CELL_EXPOSED_BACKGROUND_COLOR))
						{
							exposeCell(newButton);

						}



					}

				}
			}

			running =false;

			// what else do you need to adjust?
			// could the game be over?	// if the game is over - what else needs to be exposed / highlighte
		}

		// if the MyJButton that was just exposed has no mines in its perimeter
		// 20 pts
		if ( mineGrid[mjb.ROW][mjb.COL] == NO_MINES_IN_PERIMETER_GRID_VALUE )
		{
			for(int x = -1; x<2; x++){
				for(int y = -1; y<2; y++){

					if(!(x == 0 && y == 0) &&
							(mjb.ROW+x >= 0) && (mjb.ROW+x <MineSweapPart.MINE_GRID_ROWS) && (mjb.COL+y >= 0) && (mjb.COL+y < MineSweapPart.MINE_GRID_COLS)){
						int index = ((mjb.ROW+x)*MineSweapPart.MINE_GRID_ROWS) + mjb.COL+y;
						MyJButton newButton = (MyJButton)(mjb.getParent().getComponent(index));

						if (!newButton.getText().equals(MineSweapPart.UNEXPOSED_FLAGGED_MINE_SYMBOL)&&!newButton.getBackground().equals(CELL_EXPOSED_BACKGROUND_COLOR))
						{
							exposeCell(newButton);
						}
						// lots of work here - must expose all MyJButtons in its perimeter
						// and so on
						// and so on
						// .
						// .
						// .
						// Hint : MyJButton jbn = (MyJButton)mjb.getParent().getComponent(<linear index>);
					}
				}
			}
		}

	}
	public static void main(String[] args){
		new MineSweapPart();
	}

}


