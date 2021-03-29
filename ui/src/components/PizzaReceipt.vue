<template>
    <div :data_json="data_json" class="order-pizza-receipt">
        <div>
          <h4>Dear {{data_json.first_name}}, </h4>
          <p>Here is your order from astound pizza, </p>
          <p>Menu/Description: {{data_json.summary}}</p>
          <p>Estimated delivery time: {{data_json.deliver_time}}</p>
          <p>Delivery address: {{data_json.deliver_address}}</p>
          <p>Thank you </p>
          <p class="text-right">- Astound Pizza. </p>
        </div>
    </div>
</template>

<script>
export default {
  props: {
    data_json: {
      first_name: '',
      summary: '',
      deliver_time: '',
      delivery_address: ''
    }
  },
  methods: {}
}
</script>

<style lang="sass" scoped>
@import '@/assets/variables.scss';

.order-pizza-receipt
  font-size: 0.9em;
  width: 80%;
  border: $border;
  border-radius: $border-radius-s;
  box-shadow: $box-shadow;
  padding: 10px;
  margin: 20px 50px;
  h4
    font-size: 0.8em;
</style>
