import { Provider } from 'react-redux';
import { store } from './store/store';
import InteractionForm from './components/InteractionForm';

export default function App() {
  return (
    <Provider store={store}>
      <InteractionForm />
    </Provider>
  );
}