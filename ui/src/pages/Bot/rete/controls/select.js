import Rete from 'rete'
import Select from '../vue-control-components/Select'

class SelectControl extends Rete.Control {
  constructor (name, emitter, label) {
    super(name)
    this.component = Select
    this.props = { name, ikey: name, emitter, label }
  }

  async setValue (val) {
    this.vueContext.value = val
  }
}

export default SelectControl
