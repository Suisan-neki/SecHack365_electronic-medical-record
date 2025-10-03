import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'react-native';
import PatientDisplayScreen from './src/screens/PatientDisplayScreen';
import LoginScreen from './src/screens/LoginScreen';
import { useAppStore } from './src/store/useAppStore';

const Stack = createStackNavigator();

const App: React.FC = () => {
  const { user } = useAppStore();

  return (
    <NavigationContainer>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007bff',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {user ? (
          <Stack.Screen 
            name="PatientDisplay" 
            component={PatientDisplayScreen}
            options={{ title: '診療内容確認' }}
          />
        ) : (
          <Stack.Screen 
            name="Login" 
            component={LoginScreen}
            options={{ title: '患者情報共有システム' }}
          />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
