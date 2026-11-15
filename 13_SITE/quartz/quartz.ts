import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"

// Los componentes propios (ficha de fuente, panel de avance y anotaciones) se
// cargan como plugins locales desde `quartz-plugins/`, igual que los del
// registro de npm. Antes de compilar hay que crear los enlaces de
// `.quartz/plugins/` con `09_AUTOMATION/preparar_plugin_sitio.cmd`: en Windows
// el symlink que haría Quartz por su cuenta falla con EPERM sin privilegios.

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
