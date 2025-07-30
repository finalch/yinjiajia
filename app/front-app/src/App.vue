<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div id="app">
    
    
    <main class="main-content">
      <router-view />
    </main>
    <nav class="navbar">
      <router-link to="/" class="nav-link">商城</router-link>
      <router-link to="/cart" class="nav-link">购物车</router-link>
      <router-link to="/my-order" class="nav-link">我的订单</router-link>
      <router-link to="/customer-service" class="nav-link">客服</router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background-color: #fff;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #f0f0f0;
}

.nav-link.router-link-active {
  background-color: #007bff;
  color: white;
}

.main-content {
  flex: 1;
  padding: 1rem;
}
</style>
