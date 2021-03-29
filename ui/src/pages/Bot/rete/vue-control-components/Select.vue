<template>
  <div class="control-holder row"
    @mousedown="disablePropergation($event)"
    @click="disablePropergation($event)">
    <label class="col-3">{{label}}</label>
    <input class="col-9"
      :name="name"
      :value="value"
      @change="change($event)"
      :options="allActions"
      :searchable="false" />
  </div>
</template>

<script>
import axios from 'axios'
const ILLUSIONIST_PORT = process.env.VUE_APP_ILLUSIONIST_PORT
const baseUrl = 'http://' + window.location.hostname + ':' + ILLUSIONIST_PORT + '/api'

export default {
  props: ['name', 'emitter', 'ikey', 'getData', 'putData', 'label'],
  data () {
    return {
      value: '',
      readOnly: false,
      isNodeTitle: false,
      allActions: []
    }
  },
  methods: {
    change (e) {
      this.value = e.target.value
      this.putData(this.ikey, this.value)
    },
    disablePropergation (e) {
      if (this.name !== 'name') {
        e.stopImmediatePropagation()
      }
    },
    readBotActions () {
      var vm = this
      axios
        .request({
          method: 'get',
          url: baseUrl + '/action?results_per_page=9999'
        })
        .then((response) => {
          if (response.status === 200) {
            response.data.objects.forEach((obj) => {
              vm.allActions.push(obj.name)
            })
          } else {
            console.warning('Failed loading actions')
          }
        })
    }
  },
  mounted () {
    this.value = this.getData(this.ikey)
    this.readBotActions()
  }
}
</script>
