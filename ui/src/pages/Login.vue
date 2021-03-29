<template>
  <b-container fluid>
    <b-row class="text-center">
      <b-col>
        <img class="logo" :src='logo' />
        <h1>{{title}}</h1>
      </b-col>
    </b-row>
    <div class="login">
      <b-form @submit.prevent="loginUser">
        <b-form-group label="Username" label-for="username">
          <b-form-input id="username" type="text" v-model="username" required placeholder="Enter username" />
        </b-form-group>
        <b-form-group label="Password" label-for="password">
          <b-form-input id="password" type="password" v-model="password" required placeholder="Enter password" />
        </b-form-group>
        <b-row class="row">
          <b-button class="submit" type="submit" variant="success">Login</b-button>
        </b-row>
      </b-form>
    </div>
  </b-container>
</template>

<script>
import { illusionistAPI } from '../utils/rest-config'

export default {
  data: function () {
    return {
      username: '',
      password: '',
      title: 'Illusionist Login',
      logo: require('@/assets/logo.png')
    }
  },
  methods: {
    loginUser () {
      const payload = {
        username: this.username,
        password: this.password
      }
      const vm = this
      illusionistAPI
        .post('/users/login', payload)
        .then((response) => {
          window.localStorage.setItem('access_token', response.data.payloads.access_token)
          illusionistAPI.get('/users/me')
            .then((response) => {
              window.localStorage.setItem('user_id', response.data.payloads.data.id)
              window.localStorage.setItem('username', response.data.payloads.data.username)
              window.localStorage.setItem('first_name', response.data.payloads.data.first_name)
              window.localStorage.setItem('last_name', response.data.payloads.data.last_name)
              window.localStorage.setItem('roles', JSON.stringify(response.data.payloads.data.roles))
              if (vm.$route.params.redirectPath) {
                vm.$router.push(this.$route.params.redirectPath)
              } else {
                vm.$router.push('/admin')
              }
            })
        })
    }
  }
}
</script>

<style lang="sass">
@import "@/assets/action.sass";

.logo
  margin: 1em;
  height: 50px;
  width: auto;
.login
  width: 30%;
  margin: 0 auto;
  .submit
    margin: 0 auto;
</style>
