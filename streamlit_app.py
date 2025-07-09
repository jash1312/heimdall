import streamlit as st
from main import fetch_prices

st.title('Online Product Price Aggregator')

st.write('Enter a product name and country to fetch the best prices from multiple websites.')

country = st.selectbox('Country', ['IN', 'US'])
query = st.text_input('Product Name', '')

if st.button('Fetch Prices'):
    if not query.strip():
        st.warning('Please enter a product name.')
    else:
        with st.spinner('Fetching prices...'):
            try:
                results = fetch_prices(country, query)
                results = results[:2]  # Only top 2
                if results:
                    st.success(f'Top {len(results)} results:')
                    for r in results:
                        st.markdown(f"**{r['productName']}**  ")
                        st.markdown(f"Price: {r['price']} {r['currency']}")
                        st.markdown(f"Source: {r.get('source', '')}")
                        st.markdown(f"[View Product]({r['link']})")
                        st.markdown('---')
                else:
                    st.info('No results found.')
            except Exception as e:
                st.error(f'Error: {e}') 