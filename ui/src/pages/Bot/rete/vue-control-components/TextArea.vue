<template>
  <div class="control-holder row"
    @mousedown="disablePropergation($event)"
    @click="disablePropergation($event)">
    <label v-if="!isNodeTitle" class="col-3">{{label}}</label>
    <textarea class="col-9"
      :name="name"
      :value="value"
      @input="change($event)"
      :readonly="readOnly"
      :placeholder="placeholder"
      :autocomplete="autocomplete"/>
  </div>
</template>

<script>
export default {
  props: ['name', 'emitter', 'ikey', 'getData', 'putData', 'label'],
  data () {
    return {
      value: [],
      readOnly: false,
      isNodeTitle: false,
      autocomplete: 'on',
      placeholder: ''
    }
  },
  methods: {
    change (e) {
      var value = e.target.value
      this.value = value
      if (this.isJSON(value)) {
        this.putData(this.ikey, JSON.parse(value))
      } else {
        this.putData(this.ikey, value)
      }
    },
    isJSON (str) {
      try {
        return (JSON.parse(str) && !!str)
      } catch (e) {
        return false
      }
    },
    disablePropergation (e) {
      e.stopImmediatePropagation()
    }
  },
  mounted () {
    var value = this.getData(this.ikey)
    if (typeof (value) === 'object') {
      this.value = JSON.stringify(value, null, 4)
    } else {
      this.value = value
    }
  }
}
</script>
