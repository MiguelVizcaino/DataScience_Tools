import streamlit as st

def main():
    st.title("Proyecto Final")
    st.subheader("Bienvenido a mi aplicación")
    st.write("Este es un ejemplo básico de una aplicación en Streamlit.")
    st.button("Haz clic aquí")
    st.text_input("Ingresa un texto:")
    st.slider("Selecciona un valor:", 0, 100)

if __name__ == '__main__':
    main()
