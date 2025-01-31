# Wave Generator with Tkinter

This project is a graphical application built with Python's Tkinter library to visualize sine waves and allow user interaction through various controls. It demonstrates the use of sliders, text boxes, and dropdown menus to manipulate and display sine wave functions and bitstream data.

## Features

- **Sine Wave Visualization**: Draws a sine wave on a canvas based on frequency, amplitude, and offset values.
- **Noise Function Input**: Allows the user to input a custom noise function.
- **Bitstream Input**: Lets users input a bitstream and select physical and link layer protocols.
- **Interactive Controls**: Includes sliders for frequency, amplitude, and offset, as well as dropdown menus for protocol selection.

## Installation

1. Ensure you have Python installed on your system.
2. Clone the repository or download the code.
3. Install Tkinter if it's not already included in your Python installation. Tkinter usually comes pre-installed with Python, but if needed, you can install it using:

   ```sh
   pip install tk
   ```

## Usage

1. Run the application using Python:

   ```sh
   python interface.py
   ```

2. The application window will open with the following controls:
   - **Frequency Slider**: Adjusts the frequency of the sine wave.
   - **Amplitude Slider**: Adjusts the amplitude of the sine wave.
   - **Offset Slider**: Adjusts the offset of the sine wave.
   - **Noise Function Text Box**: Input a noise function to be visualized.
   - **Bitstream Text Box**: Input a bitstream for protocol selection.
   - **Physical Layer Selector**: Dropdown menu to select the physical layer protocol.
   - **Link Layer Selector**: Dropdown menu to select the link layer protocol.

3. Use the sliders to modify the sine wave parameters and see the changes in real-time.
4. Enter a noise function and click "Send" to update the visualization.
5. Enter a bitstream and select protocols to configure the data for visualization.

## Code Overview

- **Event Handlers**:
  - `on_selectFisica(event)`: Handles selection changes in the physical layer dropdown.
  - `on_selectEnlace(event)`: Handles selection changes in the link layer dropdown.
  - `bitstram_set()`: Updates the bitstream variable with the content from the bitstream text box.
  - `functset()`: Updates the noise function and redraws the sine wave.
  - `update_Freq(value)`, `update_Amp(value)`, `update_Offset(value)`: Update the frequency, amplitude, and offset based on slider values.

- **Wave Functions**:
  - `parsefunction(x, numeroPontos)`: Parses the noise function string and generates wave data.
  - `num(x, function)`: Computes the wave values for a given function.
  - `functionvalue(x, function)`: Aggregates wave data for multiple functions.

- **Drawing Functions**:
  - `draw_center_lines()`: Draws center lines on the canvas.
  - `draw_sine_wave()`: Draws the sine wave on the canvas based on current slider values and noise function.

- **GUI Components**:
  - `tk.Canvas`: The canvas widget where the sine wave is drawn.
  - `tk.Scale`: Sliders for adjusting frequency, amplitude, and offset.
  - `ttk.Combobox`: Dropdown menus for protocol selection.
  - `tk.Text` and `tk.Button`: Text boxes and buttons for input and interaction.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

