<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" size="icon">
        <Globe class="h-5 w-5" />
        <span class="sr-only">{{ localeName }}</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-40">
      <DropdownMenuItem
        v-for="locale in availableLocales"
        :key="locale"
        class="flex items-center justify-between"
        @click="setLocale(locale)"
      >
        <span>{{ getLanguageName(locale) }}</span>
        <Check v-if="currentLocale === locale" class="h-4 w-4 text-primary" />
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup>
import { Globe, Check } from "lucide-vue-next";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useI18n } from "../composables/useI18n";

const { currentLocale, setLocale, availableLocales, localeName } = useI18n();

const languageNames = {
  en: "English",
  ja: "\u65E5\u672C\u8A9E",
};

const getLanguageName = (locale) => {
  return languageNames[locale] || locale;
};
</script>
