import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

st.set_page_config(page_icon="👨‍🔬")

PTABLE = pd.read_csv("Periodic Table of Elements.csv")


def find_electrons(element_symbol):
    element_data = PTABLE[PTABLE["Symbol"] == element_symbol.capitalize()]
    if not element_data.empty:
        electrons = element_data["NumberofElectrons"].iloc[0]
        return electrons
    else:
        return None


# ELECTRON CONFIGURATION!!!
def electron_configuration(num_electrons):
    orbitals = [
        "1s",
        "2s",
        "2p",
        "3s",
        "3p",
        "4s",
        "3d",
        "4p",
        "5s",
        "4d",
        "5p",
        "6s",
        "4f",
        "5d",
        "6p",
        "7s",
        "5f",
        "6d",
        "7p",
    ]

    electron_count = 0
    orbital_index = 0
    electron_contents = {}

    while electron_count < num_electrons and orbital_index < len(orbitals):
        orbital = orbitals[orbital_index]
        if orbital.endswith("s"):
            max_electrons = 2
        elif orbital.endswith("p"):
            max_electrons = 6
        elif orbital.endswith("d"):
            max_electrons = 10
        elif orbital.endswith("f"):
            max_electrons = 14
        electrons_added = min(num_electrons - electron_count, max_electrons)

        # fill the orbital with electrons and their spin direction
        for i in range(electrons_added):
            if orbital not in electron_contents:
                electron_contents[orbital] = {"up": 0, "down": 0}
            if electron_contents[orbital]["up"] < max_electrons // 2:
                electron_contents[orbital]["up"] += 1
            else:
                electron_contents[orbital]["down"] += 1
            electron_count += 1

        orbital_index += 1

    return electron_contents


def compute_quantum_numbers(electron_configuration_dict):
    quantum_numbers = {}
    for orbital, electrons in electron_configuration_dict.items():
        n = int(re.findall(r"\d+", orbital)[0])
        l = 0 if orbital.endswith("s") else n - 1
        m_values = list(range(-l, l + 1))
        m_index = 0

        for spin, count in electrons.items():
            for _ in range(count):
                m = m_values[m_index % len(m_values)]
                m_index += 1
                s = 1 / 2 if spin == "up" else -1 / 2
                if orbital not in quantum_numbers:
                    quantum_numbers[orbital] = []
                quantum_numbers[orbital].append({"n": n, "l": l, "m": m, "s": s})
    return quantum_numbers


def plot_electrons(quantum_numbers):
    fig = go.Figure()
    for orbital, electrons in quantum_numbers.items():
        for electron in electrons:
            n = electron["n"]
            l = electron["l"]
            m = electron["m"]
            s = electron["s"]
            fig.add_trace(
                go.Scatter3d(
                    x=[n],
                    y=[l],
                    z=[l + m],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=(
                            "blue" if s == 0.5 else "red"
                        ),  # Adjust color based on spin
                        opacity=0.8,
                    ),
                    name=f"({n}, {l}, {l + m})",
                )
            )
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="x: Principal (n)"),
            yaxis=dict(title="y: Angular Momentum (l)"),
            zaxis=dict(title="z: Magnetic (m)"),
            aspectratio=dict(x=1, y=1, z=1),
        )
    )
    st.plotly_chart(fig)


def convert_to_latex(configuration):
    latex_string = r"\begin{align*}"

    for orbital, spins in configuration.items():
        latex_string += rf"{orbital}: & \quad "
        if spins["up"] > 0:
            latex_string += rf"{spins['up']}\uparrow"
        if spins["down"] > 0:
            if spins["up"] > 0:
                latex_string += " \\quad "
            latex_string += rf"{spins['down']}\downarrow"
        latex_string += r"\\"

    latex_string += r"\end{align*}"
    return latex_string


def convert_to_standard_notation(configuration):
    notation = ""
    for orbital, spins in configuration.items():
        total_spins = spins["up"] + spins["down"]
        if total_spins > 0:
            notation += f"${orbital}^{{{total_spins}}}$"

    # Add space between each orbital notation
    notation_with_spaces = " ".join(notation.split("$")[1:])

    return notation_with_spaces


def create_quantum_numbers_table(quantum_numbers):
    data = []
    columns = ["Orbital", "Electron", "n", "l", "m", "s"]

    for orbital, electrons in quantum_numbers.items():
        for i, electron in enumerate(electrons, 1):
            n = electron["n"]
            l = electron["l"]
            m = electron["m"]
            s = electron["s"]
            data.append([orbital, i, n, l, m, s])

    df = pd.DataFrame(data, columns=columns)
    return df


st.title("quantum-numbers-of-electons 👨‍🔬")
st.image("Science-cuate.png")
st.divider()

st.header("Description")
st.subheader("What are quantum numbers?")
st.write(
    "An electron has four quantum numbers, each describing a feature of the electron. The four quantum numbers are the principal quantum number, angular momentum quantum number, magnetic quantum number, and the spin quantum number."
)
st.subheader("Principal (n)")
st.write("Indicates energy level for an electron. Range: positive integers 1,2,3,...")
st.subheader("Angular momentum (l)")
st.write(
    "One integer corresponding to an electron’s orbital shape (s,p,d,f). Range for principal number n: integers from 0 until (n-1); 0,1,2,3,...(n-1)"
)
st.subheader("Magnetic (m)")
st.write(
    "Possible orientations of an electron’s orbital of shape l. Range for angular momentum number l: integers -l,...,-1,0,1,...,l."
)
st.write(
    " *in the model, a m value is assigned to an electron’s orbital based on its position in the range -l,...,-1,0,1,...,l. For example, the first orbital in the l subshell will have orientation -l, the second will have -l+1 and so on until the last orbital receives orientation l."
)
st.subheader("Spin (s)")
st.write("The spin of an electron. Possible values: +1/2(up),-1/2(down)")


st.header("Element Input")
element = st.text_input("Element Symbol (e.g. Fe)")

if element:
    num_electrons = find_electrons(element)

    if num_electrons is not None:
        st.write(f"Number of electrons: {num_electrons}")
        configuration = electron_configuration(num_electrons)
        quantum_numbers = compute_quantum_numbers(configuration)
        print(configuration)
        st.header("Orbital Notation")
        st.latex(convert_to_latex(configuration))
        st.header("Standard Notation")
        st.latex(convert_to_standard_notation(configuration))
        st.header(f"Quantum Numbers for Each Electron in {element}")
        quantum_numbers_df = create_quantum_numbers_table(quantum_numbers)
        st.dataframe(quantum_numbers_df)
        st.header("Wicked Cool Graph of All Electron Quantum Numbers")
        st.write("In the form (n,l,m)")
        st.write("🟦 indicates spin up")
        st.write("🟥 indicates spin down")
        print(quantum_numbers)
        plot_electrons(quantum_numbers)
    else:
        st.write("That's not an element, doofus")
